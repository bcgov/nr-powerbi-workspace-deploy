# nr-power-bi-workspace-deploy
This repository automates publishing Power BI .pbix files to the NRS Analytics Power BI workspaces, using GitHub actions.

## GitHub Process Overview:
1. Reach out to NRM.DataFoundations@gov.bc.ca to gain 'Write' access to this repo
2. Submit a PR with the Power BI file you want to publish (make sure to place the .pbix file under the folder that aligns with the workspace you want to publish to)
3. A member of Data Foundations will review your PR. Once a PR is approved, the dashboard is published to the corresponding workspace

## S3 File System Process Overview:
1. Reach out to NRM.DataFoundations@gov.bc.ca to gain access to S3 object storage
2. Place PBI report in object storage following this file convention: {env}/{domain}/{report_name}.pbix
3. Maintain list of IDIR users who should have report access in the users.txt file
4. Access report publication history at {env}/{domain}/archive/

## Limitations: 
- There is a ~ 1 hour lag in deployments from S3 File System. This is due to sync delay between GeoDrive and S3.
- **Do not publish .pbix files in GitHub unless the  Power BI report is public-facing.** Power BI reports with up to Protected B data can be deployed from S3 object storage (see above).
- Based on the Power BI API documentation, this workflow should be suitable for Power BI .pbix files that are up 10 GB in size.
