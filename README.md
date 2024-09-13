# Flask Feedback Form

![Python](https://img.shields.io/badge/-Python-333333?style=flat&logo=python)
![Flask](https://img.shields.io/badge/-Flask-333333?style=flat&logo=flask)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-333333?style=flat&logo=postgresql)

Flask Feedback Form is a web application designed to collect and analyze feedback and ratings for multiple teams.

Check out the live website [here](https://flaskfeedbackform.bhuvansa.com).

## Table of Contents

-   [Features](#features)
-   [Installation](#installation)
-   [Usage](#usage)
-   [System Architecture](#system-architecture)
-   [DBML Diagram](#dbml-diagram)
-   [Credits](#credits)
-   [License](#license)

## Features

-   Users can submit feedback for multiple teams by filling out a form with their name, rating, and feedback message.
-   Interactive dashboard displaying insights into ratings and feedback that have been submitted.
-   Authentication functionality to prevent unauthorized access to the dashboard.

## Installation

1. Clone the repository to your local machine.
2. Create a `.env` file in the root directory with the following data:

    ```
    # Application Details
    FEEDBACK_FORM_ADMIN_USERNAME=YOUR_ADMIN_USERNAME
    FEEDBACK_FORM_ADMIN_PASSWORD=YOUR_ADMIN_PASSWORD
    FEEDBACK_FORM_SECRET_KEY=YOUR_SECRET_KEY

    # PostgreSQL database details
    FEEDBACK_FORM_DB_HOST=db
    FEEDBACK_FORM_DB_NAME=YOUR_DATABASE_NAME
    FEEDBACK_FORM_DB_USER=YOUR_DATABASE_USERNAME
    FEEDBACK_FORM_DB_PASSWORD=YOUR_DATABASE_PASSWORD
    ```

3. Build and start the application using Docker Compose:

    ```sh
    docker-compose up --build
    ```

## Usage

-   Visit `http://localhost:3000/` to submit feedback.
-   Visit `http://localhost:3000/dashboard` to view data.

## System Architecture

![System Architecture](./public/static/images/Architecture_diagram.svg)

## DBML Diagram

![DBML Diagram](https://kroki.io/dbml/svg/eNqNkE2OwjAMRvc9RZawGfG7YcEhEDuEKpd-LRZJxLhpR2g0dyeNJm2EALFJYr_E9sueCg0l6Bg_EPWbqSHIuVQNhEmrw1XYkNzUBbdjesWSgepITmeSyXI2HVju2JN-aRyZa_aXZfvQyoFMaNMf3rQI2Lam8FOxdaj9fmgtf7c4jtUqoCzodGlCyRh9Mrm_8l82mWXMVAxdznMhx7ZWjSGtPYxg8QosX4HVE0AdhGpEIiCdSAzfulivp73xDtVmFP5KTbaDV5p-fBEtt8E3hncIU7Tx)

## Credits

This project was created by [Nishith P Shetty](https://github.com/nishith-p-shetty) and [Bhuvan S A](https://github.com/BhuvanSA).

## License

This project is licensed under the terms of the [GNU GENERAL PUBLIC LICENSE](LICENSE).
