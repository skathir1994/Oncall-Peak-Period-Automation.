# Oncall-Peak-Period-Automation.

Problem:  The oncall team is addressing VM rejections in Andon tickets. In the daily allocation and on tickets issued to auditors. By load the ticket URLs and found the rejected ASIN, Marketplace, and Merchant ID. By using the pricing rules, load the ASIN, and then choose the rejected marketplace. Then only auditors knew the reasons for rejections and rejections against competitors. Auditors then validate the rejections. Resolve the andon tickets based on the validation findings. This approach takes more time to find the rejection information. This has an impact on the auditor's daily target of 50 tickets.

Proposed Solution: I identified these issues and found solutions. 
Open the https://issues.amazon.com/ site, select the ASIN Metrics folder and the Open status, and then export the andon open tickets with the necessary information. It includes the ticket id, VM id, overview information (ASIN, Marketplace Id, Merchant Id), and the creation date. Then I used the concat function to concatenate ASIN, Marketplace Id, Merchant Id, and VM ID. 
I wrote and ran the SQL query to retrieve rejection data from the pricing rejects database. And by looking up the oncall and price rejects data, I can extract the rejection information. 
I wrote Python code to implement the complete technique mentioned above. The data gets generated with a single click and shared to the oncall team DLs via Outlook.

Impact:  During peak day, the on-call team must prioritize deal ASINs that must be addressed within the 10-hour SLA. Using the automation mentioned above throughout the sale period the oncall team met their SLA of 3 hours rather than 10 hours. 
And this automation data helps the on-call crew in resolving tickets using bulk closing techniques. This had a direct impact on on-call HCs utilization. This data also reduced the auditor's validation times. 

