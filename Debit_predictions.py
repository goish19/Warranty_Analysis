import pandas as pd
import numpy as np
import os
import csv


##Enter file Path
file=r""
##Enter sheet name
sheet=""
df= pd.read_excel(file,sheet_name=sheet)
df["Part_Number_9"]=df["Parts No"].astype(str).str[:9]
df["Posting YM"] = pd.to_datetime(df["Posting YM"], errors="coerce")
df["Build_date"] = pd.to_datetime(df["Production YM"]).dt.strftime("%Y-%m")

def final_debits(df, partno, posting_month,TF):
    TF = TF
    df1 = df.copy()
    # Partno filter
    df1 = df1[df1["Part_Number_9"] == partno]
    ##postingmonth claims
    post_month_claims=(df1["Posting YM"]==posting_month).sum()
    # average and technical factor calc
    mean_cost =round(df1["Current Total Claim Amt"].mean(),2)
    # Masking data for 36 posting months
    start = pd.to_datetime(posting_month,format="%Y-%m-%d", errors="raise") - pd.DateOffset(months=35)
    df1 = df1[
        (pd.to_datetime(df1["Posting YM"], errors="coerce") >= start) 
    ]
    df_countclaims = df1.groupby("Build_date")["Veh ID Nbr"].count()
    # 1st Iteration to remove outliers
    q3 = df_countclaims.quantile(0.75)
    q2 = df_countclaims.quantile(0.25)
    IQR = q3 - q2
    UCL =round((q3+ (1.5 * IQR)),0)
    df_countclaims = df_countclaims[df_countclaims < UCL]
    # 2nd Iteration
    q3 = df_countclaims.quantile(0.75)
    q2 = df_countclaims.quantile(0.25)
    IQR = q3 - q2
    UCL =round((q3+ (1.5 * IQR)),0)
    df_countclaims = df_countclaims[df_countclaims > UCL]
   # Total claims after 2nd iteration
    df_countclaims = (
    df1.groupby("Build_date")["Veh ID Nbr"]
       .count()
       .reset_index(name="counts")
    )
    #### The claims after fixing our UCL How many claims are more than the UCL we get charged for it
    df_countclaims=df_countclaims[df_countclaims["counts"]>UCL]
    df_countclaims["counts"]=df_countclaims["counts"]-UCL
    claims_above_UCL=round(df_countclaims["counts"].sum(),1)
    #cost to supplier
    cost_to_supplier =round( TF * claims_above_UCL * mean_cost,2)
    ## Calculate Debit  paid is charged (predicted)
    if post_month_claims<claims_above_UCL:
        Debit=mean_cost*TF*post_month_claims
    else:
        Debit=mean_cost*TF*claims_above_UCL
    ### Print areas
    print(f" ___The partno is: {partno}__")
    print(f"Claims above ucl is: {claims_above_UCL}")
    print(f"The {TF*100} % average cost is: {mean_cost*TF}")
    print(f"Debit predicted : {round(Debit,2)}K$")
    print(f"posting Month claims : {post_month_claims}")
    return cost_to_supplier

## list part nos to 
Partno_list=["",""]
## Enter the posting month
posting_month = ""
## Enter the TF
TF=
for partno in Partno_list:
    result = final_debits(df, partno, posting_month,TF)



