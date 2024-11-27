USE DBProject
GO
CREATE PROCEDURE PlaceOrder
    @user_id INT,
    @is_pickup BIT,
    @total_cost DECIMAL(10, 2)
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;

    BEGIN TRY
        DECLARE @order_id INT, @vendor_id INT;
        DECLARE @item_id INT, @quantity INT, @price_per_unit DECIMAL(6, 2);
        DECLARE @insufficient_stock_item VARCHAR(100);

        -- Validate cart is not empty
        IF NOT EXISTS (SELECT 1 FROM Cart WHERE user_id = @user_id)
        BEGIN
            RAISERROR('Cannot place order with an empty cart', 16, 1);
            RETURN;
        END

        -- Validate stock availability
        SELECT TOP 1 @insufficient_stock_item = mi.item_name
        FROM Cart c
        JOIN Menu_Items mi ON c.item_id = mi.item_id
        WHERE c.quantity > mi.units_in_stock;

        IF @insufficient_stock_item IS NOT NULL
        BEGIN
            RAISERROR('Insufficient stock for item: %s', 16, 1, @insufficient_stock_item);
            RETURN;
        END

        -- Get vendor ID
        SELECT TOP 1 @vendor_id = mi.vendor_id
        FROM Cart c
        JOIN Menu_Items mi ON c.item_id = mi.item_id
        WHERE c.user_id = @user_id;

        -- Insert order
        INSERT INTO Orders (
            user_id, vendor_id, is_pickup, 
            total_cost, order_placed, status
        )
        VALUES (
            @user_id, @vendor_id, @is_pickup, 
            @total_cost, GETDATE(), 'Pending'
        );

        SET @order_id = SCOPE_IDENTITY();

        -- Process cart items
        DECLARE cart_cursor CURSOR LOCAL FOR 
        SELECT c.item_id, c.quantity, mi.price
        FROM Cart c
        JOIN Menu_Items mi ON c.item_id = mi.item_id
        WHERE c.user_id = @user_id;

        OPEN cart_cursor;
        FETCH NEXT FROM cart_cursor INTO @item_id, @quantity, @price_per_unit;

        WHILE @@FETCH_STATUS = 0
        BEGIN
            -- Insert order details
            INSERT INTO Order_Details (
                order_id, item_id, quantity, price_per_unit
            )
            VALUES (
                @order_id, @item_id, @quantity, @price_per_unit
            );

            -- Update menu item stock
            UPDATE Menu_Items
            SET units_in_stock = units_in_stock - @quantity
            WHERE item_id = @item_id;

            FETCH NEXT FROM cart_cursor INTO @item_id, @quantity, @price_per_unit;
        END

        CLOSE cart_cursor;
        DEALLOCATE cart_cursor;

        -- Deduct from user balance
        UPDATE Users
        SET current_balance = current_balance - @total_cost
        WHERE user_id = @user_id;

        -- Record balance history
        INSERT INTO User_Balance_History (
            user_id, amount, is_deposit, 
            record_date, physical_payment, order_id, admin_id
        )
        VALUES (
            @user_id, @total_cost, 0, 
            GETDATE(), 0, @order_id, NULL
        ); 

        -- Clear user's cart
        DELETE FROM Cart 
        WHERE user_id = @user_id;

        -- Create notification
        INSERT INTO Notifications (
            user_id, notif_type, notif_content, 
            priority, order_id, sent_at
        )
        VALUES (
            @user_id, 1, 
            'Your order has been placed successfully.', 
            1, @order_id, GETDATE()
        );

        COMMIT TRANSACTION;
        SELECT @order_id AS OrderId;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        DECLARE @ErrorMessage NVARCHAR(4000), 
                @ErrorSeverity INT, 
                @ErrorState INT;
        
        SELECT 
            @ErrorMessage = ERROR_MESSAGE(), 
            @ErrorSeverity = ERROR_SEVERITY(), 
            @ErrorState = ERROR_STATE();
        
        RAISERROR (
            @ErrorMessage, 
            @ErrorSeverity, 
            @ErrorState
        );
    END CATCH;
END;


GO
CREATE PROCEDURE DepositMoney
    @user_id INT,
    @deposit_amount DECIMAL(10, 2)
AS
BEGIN
    BEGIN TRANSACTION;

    BEGIN TRY

        IF @deposit_amount < 500
        BEGIN
            RAISERROR('Deposit amount must be greater than 500.', 16, 1)
            ROLLBACK TRANSACTION
            RETURN;
        END

        -- Step 2: Update user's balance
        UPDATE Users
        SET current_balance = current_balance + @deposit_amount
        WHERE user_id = @user_id;

        -- Step 3: Insert record into User_Balance_History
        INSERT INTO User_Balance_History (
            user_id, 
            amount, 
            is_deposit, 
            record_date, 
            physical_payment, 
            order_id, 
            admin_id
        )
        VALUES (
            @user_id, 
            @deposit_amount, 
            1,
            GETDATE(), 
            0,
            NULL,
            NULL
        );

        -- Commit the transaction
        COMMIT TRANSACTION;

    END TRY
    BEGIN CATCH
        -- Rollback transaction in case of an error
        ROLLBACK TRANSACTION;

        -- Raise the error
        DECLARE @ErrorMessage NVARCHAR(4000), @ErrorSeverity INT, @ErrorState INT;
        SELECT @ErrorMessage = ERROR_MESSAGE(), @ErrorSeverity = ERROR_SEVERITY(), @ErrorState = ERROR_STATE();
        RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);
    END CATCH;
END;

GO
CREATE PROCEDURE UpdateOrderStatus
    @OrderID INT,
    @Status NVARCHAR(255),
    @UserID INT
AS
BEGIN
    -- Update the order status and set the order received timestamp
    UPDATE Orders
    SET status = @Status, order_received = CURRENT_TIMESTAMP
    WHERE order_id = @OrderID;

    -- Insert a notification for the user
    INSERT INTO Notifications (user_id, notif_type, notif_content, priority, order_id, sent_at)
    VALUES (@UserID, 1, CONCAT('Order ID ', @OrderID, ' is now ', @Status), 1, @OrderID, GETDATE());
END;

