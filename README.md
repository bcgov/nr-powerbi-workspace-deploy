# nr-power-bi-workspace-deploy
This repository automates publishing Power BI .pbix files to the NRS Analytics Power BI workspaces, using GitHub actions.

## Process Overview: 
1. Reach out to NRM.DataFoundations@gov.bc.ca to gain 'Write' access to this repo
2. Submit a PR with the Power BI file you want to publish (make sure to place the .pbix file under the folder that aligns with the workspace you want to publish to)
3. A member of Data Foundations will review your PR. Once a PR is approved, the dashboard is published to the corresponding workspace.

## Pending Features: 
- Manage report access using a users.txt file
- File structure: {workspace}/{report name}/[.pbix file and users.txt file]

## Limitations: 
Based on the Power BI API documentation, this workflow should be suitable for Power BI .pbix files that are up 10 GB in size. However, large files have not been fully tested and may cause issues. 

## Action Documentation: 
(https://github.com/marketplace/actions/power-bi-pipeline-deploy)
