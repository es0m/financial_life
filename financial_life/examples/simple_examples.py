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

def house_example():
    account = a.Bank_Account(amount = 1000, interest = 0.001, name = 'Main account')
    savings = a.Bank_Account(amount = 5000, interest = 0.0013, name = 'Savings')
    loan = a.Loan(amount = 100000.00, interest = 0.0194, name = 'House Credit')
    house = a.Property(150000, 150000-loan.account, loan, name='House')

    simulation = a.Simulation(account, savings, loan, house, name = 'ES1')
    simulation.add_regular(from_acc = 'Income',
                           to_acc = account,
                           payment = 4500,
                           interval = 'monthly',
                           date_start = datetime(2020,2,16),
                           day = 23,
                           name = 'Income')

    simulation.add_regular(from_acc = account,
                           to_acc = savings,
                           payment = 100,
                           interval = 'monthly',
                           date_start = datetime(2020,2,23),
                           day = 30,
                           name = 'Savings')

    simulation.add_regular(from_acc = account,
                           to_acc= loan,
                           payment = 1482+1500,
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
    print(savings.report.yearly())
    print(loan.report.yearly())


if __name__ == '__main__':
    example1()

