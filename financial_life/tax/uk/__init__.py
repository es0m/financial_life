""" help functions for UK tax declaration """

def tax_to_pay(year, *args, **kwargs):
    """ generic functions to call the tax-function for any year. 
    This functions simply calls the year-dependent function with 
    the given parameters, but this function don't really care about
    the content of the other arguments """
    if year in tax_functions: 
        return tax_functions[year](*args, **kwargs)
    else: 
        return tax_to_pay_2019(*args, **kwargs)

def personal_allowance(taxable_pay, pa_limit):
    diff = min(max(0, taxable_pay-100000), 2*pa_limit)
    pa = pa_limit-diff/2
    return pa
        
def tax_to_pay_2019(tax_relevant_money, splitting = False):
    return tax_to_pay_generic(tax_relevant_money, 12500, [37500, 150000, 1e99], splitting)

def tax_to_pay_2018(tax_relevant_money, splitting = False):
    return tax_to_pay_generic(tax_relevant_money, 11850, [34500, 150000, 1e99], splitting)

def tax_to_pay_2017(tax_relevant_money, splitting = False):
    return tax_to_pay_generic(tax_relevant_money, 11500, [33500, 150000, 1e99], splitting)

def tax_to_pay_2016(tax_relevant_money, splitting = False):
    return tax_to_pay_generic(tax_relevant_money, 11000, [32000, 150000, 1e99], splitting)

def tax_to_pay_generic(tax_relevant_money, allowance, limits_bha, splitting):
    """ calculates the tax 
    
    Returns the tax and the percentage of the tax """
    
    if tax_relevant_money <= 0:
        return 0, 0
    
    pa_limit = allowance
    p_basic_max = limits_bha[0]
    p_higher_max = limits_bha[1]-limits_bha[0]
    p_additional_max = limits_bha[2]-limits_bha[1]
    p_basic_rate = 20
    p_higher_rate = 40
    p_additional_rate = 45
    pa = personal_allowance(tax_relevant_money, pa_limit) # e.g. 120000 -> 2500
    p0 = min(pa, tax_relevant_money)            # e.g. 2500
    pb_r = max(0, tax_relevant_money-p0)        # e.g. 117500
    p_basic = min(pb_r, p_basic_max)                 # e.g. 37500
    
    ph_r = max(0, pb_r-p_basic)
    p_higher = min(ph_r, p_higher_max)
    
    pa_r = max(0, ph_r-p_higher)
    p_additional = min(pa_r, p_additional_max)
    
    tax = float(int(p_basic_rate*p_basic + p_higher_rate*p_higher + p_additional_rate*p_additional))/100
    tax_rate = tax/tax_relevant_money
    return tax, tax_rate
    

tax_functions = {
    2019: tax_to_pay_2019,
    2018: tax_to_pay_2018,
    2017: tax_to_pay_2017,
    2016: tax_to_pay_2016
    }
    
def cms_to_pay(year, relevant_money, qual_kids, other_kids):
    """ calculates the child maintenance amount from the gross minus pension pay
    see https://www.citizensadvice.org.uk/family/children-and-young-people/child-maintenance/child-maintenance-2012-scheme/child-maintenance-calculation/the-2012-child-maintenance-scheme-calculating-maintenance/
    
    Returns the cms and the percentage of the cms """
    
    if relevant_money <= 0 or qual_kids<=0:
        return 0, 0
        
    other_kids = max(0, other_kids)
    other_kids = min(3, other_kids)
    weekly = relevant_money/52
    print(weekly)
    if weekly<7: 
        return 0, 0.0
    if weekly<100: 
        # flat rate
        return 52*7, float(7)/weekly
    if weekly<200:
        # reduced rate
        cms = 7
        weekly_r = weekly-100
        q1_row = [17, 14.1, 13.2, 12.4]
        q2_row = [25, 21.2, 19.9, 18.9]
        q3_row = [31, 26.4, 24.9, 23.8]
        if qual_kids == 1: 
            p = q1_row[other_kids]
        if qual_kids == 2:
            p = q2_row[other_kids]
        if qual_kids >= 3: 
            p = q3_row[other_kids]
        cms = cms + float(int(weekly_r*p))/100
        return 52*cms, cms/weekly
    # basic rate:
    reduction = [0, 11, 14, 16]
    weekly_r = weekly-(int(reduction[other_kids]*weekly)/100)
    p_basic = [12, 16, 19]
    weekly_basic = min(800, weekly_r)
    cms_basic = float(weekly_basic*p_basic[qual_kids-1])/100
    print('basic:' + str(cms_basic))
    
    if weekly_r <= 800.00: 
        return 52*cms_basic, 1.0*cms_basic/weekly
        
    # basic plus rate: 
    weekly_r_plus = weekly_r-800
    p_basic_plus = [9, 12, 15]
    cms_basic_plus = float(weekly_r_plus*p_basic_plus[qual_kids-1])/100
    print('basic plus:' + str(cms_basic_plus))
    
    cms_full = cms_basic + cms_basic_plus
    return 52*cms_full, float(cms_full)/weekly
    

