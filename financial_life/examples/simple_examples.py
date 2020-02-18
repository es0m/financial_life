'''
Created on 14.08.2016

@author: martin
'''
# standard libraries
from datetime import timedelta, datetime
import os

# third-party libraries
from matplotlib.pyplot import show

# own libraries
from financial_life.financing import accounts as a
from financial_life.reports import html


from dateutil.relativedelta import relativedelta

def example1():
    # create a private bank account and a loan
    start_date = datetime(2020, 1, 1)
    mortgage_payment = 1500
    account = a.Bank_Account(amount = 1000, interest = 0.00, name = 'Main account', date = start_date)
    account.set_monthly_interest()
    savings = a.Bank_Account(amount = 250, interest = 0.025, name = 'Savings 2.5', date = start_date)
    savings.set_monthly_interest()
    loan = a.Loan(amount = 100000, interest = 0.02, name = 'Mortgage', date = start_date)
    
    loan.set_monthly_interest()

    # add these accounts to the simulation
    simulation = a.Simulation(account, loan, savings, date=start_date)#, loan)

    # describe single or regular payments between accounts. note, that
    # a string can be used for external accounts that you don't want to model.
    # also note the lambda function for the payments to the loan.
    simulation.add_regular('Income', account, 4500, interval = 'monthly', date_start = start_date)
    # you can also use lambda function to dynamically decide how much money
    # you would like to transfer
    max_surplus = 500
    diff = 500
    for i in range(12) : 
        simulation.add_unique(account, savings, max_surplus-diff, date = start_date + relativedelta(months=i))
    #simulation.add_regular(account, savings, 250, date_stop = lambda x: x>datetime(2021,1,1), interval = 'monthly')
    
    simulation.add_unique(savings, account, lambda: savings.account, date = start_date + relativedelta(months=12))
    simulation.add_regular(account, loan, lambda: min(mortgage_payment+diff, -loan.account), interval = 'monthly')

    # simulate for ten years
    simulation.simulate(delta = start_date + relativedelta(years=25) - start_date)#timedelta(days=365*2+1))
    # plot the data
    simulation.plt_summary()
    #show()

    # print reports summarized in years
    #print(account.report.monthly().as_df())
    #print(savings.report.monthly().as_df())
    print(loan.report.yearly().as_df())

    # analyze data
    print("Interests on bank account: %.2f" % sum(account.report.monthly().interest))
    print("Interests on loan account: %.2f" % sum(loan.report.monthly().interest))
    print("Interests on savings account: %.2f" % sum(savings.report.monthly().interest))
    print("total interests: %.2f" % (sum(loan.report.monthly().interest) + sum(savings.report.monthly().interest)) )

    return simulation

def example2():
    # create a private bank account and a loan
    account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
    savings = a.Bank_Account(amount = 5000, interest = 0.007, name = 'Savings')
    loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit')

    # add these accounts to the simulation
    simulation = a.Simulation(account, savings, loan)

    # describe single or regular payments between accounts. note, that
    # a string can be used for external accounts that you don't want to model.
    # also note the lambda function for the payments to the loan.
    simulation.add_regular('Income', account, 2000, interval = 'monthly')
    simulation.add_regular(account, savings, 500, interval = 'monthly')
    simulation.add_regular(account, loan, lambda: min(1500, -loan.account), interval = 'monthly')
    simulation.add_unique(savings, 'Vendor for car', 10000, '17.03.2019')

    # simulate for ten years
    simulation.simulate(delta = timedelta(days=365*10))
    # plot the data
    simulation.plt_summary()

    # print reports summarized in years
    print(account.report.yearly().as_df())
    print(loan.report.yearly().as_df())
    
    # analyze data
    print("Bank account: %.2f" % (account.account + savings.account))

    cwd = os.path.dirname(os.path.realpath(__file__))
    result_folder = cwd + '/example2'

    html.report(simulation, style="standard", output_dir = result_folder)
    show()

def example3():
    account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
    savings = a.Bank_Account(amount = 5000, interest = 0.013, name = 'Savings')
    loan = a.Loan(amount = 100000, interest = 0.01, name = 'House Credit')

    simulation = a.Simulation(account, savings, loan, name = 'Testsimulation')
    simulation.add_regular(from_acc = 'Income',
                           to_acc = account,
                           payment = 2000,
                           interval = 'monthly',
                           date_start = datetime(2016,9,15),
                           day = 15,
                           name = 'Income')

    simulation.add_regular(from_acc = account,
                           to_acc = savings,
                           payment = 500,
                           interval = 'monthly',
                           date_start = datetime(2016,9,30),
                           day = 30,
                           name = 'Savings')

    simulation.add_regular(from_acc = account,
                           to_acc= loan,
                           payment = 1000,
                           interval = 'monthly',
                           date_start = datetime(2016,9,15),
                           day = 15,
                           name = 'Debts',
                           fixed = False,
                           date_stop = lambda cdate: loan.is_finished())

    simulation.add_regular(from_acc = account,
                           to_acc= loan,
                           payment = lambda : min(8000, max(0,account.get_account()-4000)),
                           interval = 'yearly',
                           date_start = datetime(2016,11,20),
                           day = 20,
                           name = 'Debts',
                           fixed = False,
                           date_stop = lambda cdate: loan.is_finished())

    simulation.simulate(delta=timedelta(days=2000))

    simulation.plt_summary()
    show()

    print(account.report)
    print(loan.report)

def generate_positive_random_walk(start, n):
    import numpy as np
    r = np.random.randint(3, size=n-1)
    dr = (r-1)*0.175
    cr = np.insert(dr, 0, start, axis=0)
    cr = np.cumsum(cr)
    cr = np.exp(cr)/np.exp(1)
    
    #for i, d in enumerate(dr):
    #    cr[i+1] = max(0.0, cr[i] + d)
    return cr

def generate_set_of_walks(start, n, size): 
    import numpy as np
    a = np.zeros((n, size), dtype=np.float)
    for i in range(size):
        cr = generate_positive_random_walk(start, n)
        a[:,i] = cr.T
    return a
    
def get_percentiles(A, percentiles):
    import numpy as np
    sz = A.shape[0]
    layers = np.empty((sz, len(percentiles)-1))
    p = np.asarray(percentiles)
    pcts = np.floor(p*(A.shape[1]-1))
    pcts = pcts.astype(np.int)
    for i in range(sz) : 
        _sorted = np.sort(A[i,:])
        cs = np.cumsum(_sorted)#/_sorted.shape[0]
        dcs = cs[pcts[1:]]-cs[pcts[0:-1]]
        dn = pcts[1:]-pcts[0:-1]
        layers[i, :] = np.divide(dcs, dn)#cs[pcts],pcts)#_sorted[pcts]
        #layers[i, :] = _sorted[pcts]
    return layers

#def interest_per_quarter(quarter, interest_predictions):
    
    
def house_example():
    import numpy as np
    
    import matplotlib.pyplot as plt
    A = generate_set_of_walks(1.0, 40*4, 80)
    #percentiles = [0.25, 0.45, 0.55, 0.75]
    #percentiles = [0.0, 1.00]
    percentiles = [0.0, 0.45, 0.55, 1.00]
    layers = get_percentiles(A, percentiles)
    avg = np.mean(A, axis=1)
    colors = ["red", "green", "red"]
    for i in range(len(percentiles)-1) :
        plt.plot(np.arange(A.shape[0])/4, layers[:, i], color=colors[i])
    plt.plot(np.arange(A.shape[0])/4, avg, color="blue")
    plt.show()
    exit()
    
    for n in range(100):
        cr = generate_positive_random_walk(1.0, 100)
        #plt.plot(cr)
    plt.plot(A)
    plt.show()
    exit()
    account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
    account.set_monthly_interest()
    #savings = a.Bank_Account(amount = 5000, interest = 0.0013, name = 'Savings')
    loan = a.FixedInterestLoan(amount = 320000.00, interest_fixed = 0.0194, interest_variable=lambda loan: relativedelta(loan._current_date, loan._end_fixed).months*0.03/12, 
        time_delta = relativedelta(months=60), 
        name = 'House Credit')
    loan.set_monthly_interest()
    #loan2 = a.FixedInterestLoan(amount = 0.00, interest_fixed = 0.0144, interest_variable=0.025, date = date.now() + relativedelta(months=60), time_delta = #relativedelta(months=60), 
        #name = 'House Credit 2')
    #loan2.set_monthly_interest()
    
    house = a.Property(450000, 450000+loan.account, loan, name='House')

    simulation = a.Simulation(account, loan, house, name = 'ES1')
    simulation.add_regular(from_acc = 'Income',
                           to_acc = account,
                           payment = 4500,
                           interval = 'monthly',
                           date_start = datetime(2020,2,16),
                           day = 23,
                           name = 'Income')

    # simulation.add_regular(from_acc = account,
                           # to_acc = savings,
                           # payment = 100,
                           # interval = 'monthly',
                           # date_start = datetime(2020,2,23),
                           # day = 30,
                           # name = 'Savings')

    simulation.add_regular(from_acc = account,
                           to_acc= loan,
                           payment = 1482+500,
                           interval = 'monthly',
                           date_start = datetime(2020,3,1),
                           day = 1,
                           name = 'Debts',
                           fixed = False,
                           date_stop = lambda cdate: loan.is_finished())

    #simulation.add_regular(from_acc = account,
    #                       to_acc= loan,
    #                       payment = lambda : min(8000, max(0,account.get_account()-4000)),
    #                       interval = 'yearly',
    #                       date_start = datetime(2020,11,20),
    #                       day = 20,
    #                       name = 'Debts',
    #                       fixed = False,
    #                       date_stop = lambda cdate: loan.is_finished())

    simulation.simulate(delta=timedelta(days=365*15))

    simulation.plt_summary()
    show()

    print(account.report.yearly())
    #print(savings.report.yearly())
    print(loan.report.yearly())


if __name__ == '__main__':
    house_example()

