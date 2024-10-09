# B4 - Computer Numerical Analysis – Trade

## Project: Trading with Bots

This project aims to explore an automated trading environment by creating bots that interact with a trading server. The objective is to develop multiple client bots capable of receiving and analyzing information, making simple forecasts, and issuing buy/sell orders accordingly.

### Prerequisites

1. **Workspace Setup**: Ensure that you have set up the `ai-bot-workspace`. An installation guide is provided along with the project description.
2. **Programming Language**: You can choose the programming language you prefer to develop your bots.

### Project Steps

#### Step 1: First Simple Bot

In this first step, you will create a basic bot. A starter bot is available, which always buys a single type of currency regardless of the market conditions. However, this bot is flawed and may fail by causing illegal operations.

- **Objective**: Write a basic bot that performs a buy or sell operation 10 times, then halts for the remainder of the session.
- **Instructions**: Carefully respect the syntax so that the server understands your orders.
- **Test**: Once the bot is ready, inform the server where to find it so it can interact with it.

#### Step 2: Stock Management

Now that you have a first bot, it's time to add some essential features.

- **Objective**:
  - Store the amount of currency you own at the start, according to the server's configuration messages.
  - When issuing a buy/sell order, set the quantity to sell at half of your current stock to avoid errors.
  - Update your stocks based on your operations, considering transaction fees.
  
- **Expected Result**: The bot should not crash, but it may still lose money.

#### Step 3: Analyze and Predict

To advance further, you will need to use market information to predict future trends.

- **Objective**:
  - Store the "candles" information as soon as they are provided by the server.
  - When the bot is asked to act:
    - If the bitcoin price is rising (based on the last two values), buy as much as possible.
    - Otherwise, sell.
  
- **Code Organization**: It is recommended to clearly separate the code that handles interaction with `ai-bot-workspace` from the part that handles artificial intelligence.

### Conclusion

Once these steps are completed, your workspace will be fully set up to move on to the most interesting part of the project: implementing artificial intelligence.

### Additional Information

- **Recommended Languages**: Python, C++, Java (or any other language of your choice).
- **Documentation and Guides**: Refer to the provided guide for details on the trading server API and message formats.

### Getting Started

1. Clone the `ai-bot-workspace` project.
2. Implement the different steps described above.
3. Test your bots by connecting them to the trading server.
