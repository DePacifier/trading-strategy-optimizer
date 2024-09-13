A python trading strategy optimizer which basically:
    - fetches candle sticks data from binance
    - runs optimization using 3 optimizers one after the other using the previously found best parameters, narrowing the search space each time. Each optimization 
        - Genetic Optimization
        - Differential Optimization
        - Bayesian Optimization
    - 