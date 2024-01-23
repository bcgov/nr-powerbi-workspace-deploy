# nr-power-bi-workspace-deploy
This repository automates publishing Power BI .pbix files to the NRM Analytics Power BI workspace using GitHub actions.

Process Overview: 
1. Reach out to NRM.DataFoundations@gov.bc.ca to gain 'Write' access to this repo
2. Submit a PR with the Power BI file you want to publish (make sure to place the .pbix file under the folder that aligns with the workspace you want to publish to)
3. A member of Data Foundations will review your PR. Once approved, your dashboard is published.

Pending feature: Manage access using a users.txt file 

This workflow is suitable for Power BI .pbix files that are up 10 GB in size. 

Action documentation: https://github.com/marketplace/actions/power-bi-service-upload
