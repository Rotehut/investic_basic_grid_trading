# Parameters Configuration 

Below are the detailed explanations of each parameter used in the configuration.

### 1. System
- **Parameter:** `symbol`
- **Description:** It is the ticker to trade.
- **Example:** 
    ```plaintext
    "EURUSD"
    ```

### 2. Grid Size
- **Parameter:** `grid_size`
- **Description:** It is the price spread of the grid.
- **Example:** 
    ```plaintext
    0.00005 (will be used in grid setup as a divider)
    ```

### 3. Take Profit
- **Parameter:** `tp_size`
- **Description:** It is the take profit point for each grid since position.
- **Example:** 
    ```plaintext
    If the price to buy is 1.0000 and tp_size is 0.0005, the take_profit price will be 1.0005 (1.0000 + 0.0005).
    ```

### 4. Lower Bound
- **Parameter:** `lower_bound`
- **Description:** It is the bottom line for the grid position. The last price to buy is not below the lower bound and will be used in the formula in *create grid info*.
- **Example:** 
    ```plaintext
    1.05500
    ```

### 5. Upper Bound
- **Parameter:** `upper_bound`
- **Description:** It is the top line for the grid position. The last price to sell is not over the lower bound and will be used in the formula in *create grid info*.
- **Example:** 
    ```plaintext
    1.06500
    ```

### 6. Order Size
- **Parameter:** `order_size`
- **Description:** It is the lot to open for each grid position.
- **Example:** 
    ```plaintext
    If order_size = 0.02, it's the number of lots to open a position.
    ```

## Example of Configuration Code
Here's a snippet of how these parameters can be configured in the code.

```python
symbol = "EURUSD"
grid_size = 0.00005
tp_size = 0.00005
lower_bound = 1.05500
upper_bound = 1.06500
order_size = 0.02