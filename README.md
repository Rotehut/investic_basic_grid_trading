Configuration following parameters:

"""
symbol = "EURUSD"
grid_size = 0.00005  # Adjust this to your desired grid spread size
tp_size = 0.00005 # Adjust this to your desired grid tp size
lower_bound = 1.05500
upper_bound = 1.06500
order_size = 0.02  # Adjust this to your desired order size
current_price = 1

System
parameter: symbol, is ticker to trade,
example "EURUSD"

Grid Size
parameters: grid_size, is price spread of the grid
example "0.00005" will be used in grid setup as divider

Take Profit
parameters: tp_size, is take profit point for each grid since position
example price to buy is 1.0000 and tp_size is 0.0005 take_profit price will be 1.0005 (1.0000 + 0.0005)

Lower Bound
parameter: lower_bound, is the bottomline for the grid position
example, last price to buy is not below the lower bound and will use in the formula in  #create grid info

Upper Bound
parameter: upper_bound, is the topline for the grid position
example, last price to sell is not over the lower bound and will use in the formula in  #create grid info

Order Size
parameter: order_size, is lot to open for each grid position
example, if order size = 0.02 It's number of lot to open position

# create grid info
num_levels = int((upper_bound - lower_bound) / grid_size)
grid_prices = [lower_bound + i * grid_size for i in range(num_levels + 1)]
df = pd.DataFrame(grid_prices, columns=['price'])