import pandas as pd


if __name__ == "__main__":
    # create an empty dataframe with columns datetime, largeSum, smallSum, cumulate
    # and write it to a csv file
    col_names = ['datetime', 'largeSum', 'smallSum', 'cumulate']
    df = pd.DataFrame(columns=col_names)
    df.to_csv('deals.csv', index=False)

    col2_names = ['datetime', 'bid_ask_diffTtl', 'totalDealDiff']
    df2 = pd.DataFrame(columns=col2_names)
    df2.to_csv('pending_order.csv', index=False)

