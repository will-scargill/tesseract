![Travis (.com)](https://img.shields.io/travis/com/will-scargill/tesseract?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/will-scargill/tesseract?style=for-the-badge)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/willscargill/tesseract?style=for-the-badge)

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/will-scargill/tesseract">
    <img src="app/static/images/logo.png" alt="Logo" width="120" height="120">
  </a>

  <h3 align="center">tesseract</h3>

  <p align="center">
    Simple file hosting
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- GETTING STARTED -->
## Getting Started

To get an instance up and running follow these steps.
Recommended deployment method is via docker compose.

### Prerequisites

* [docker](https://docs.docker.com/engine/install/ubuntu/)
* [docker-compose](https://docs.docker.com/compose/install/)

### Installation

1. Create a docker-compose.yml file with the following template
   ```yaml
    version: '3.9'
    services:
      tesseract:
        container_name: tesseract
        image: willscargill/tesseract:latest
        environment:
          TESSERACT_DB_TYPE: mysql
          MYSQL_HOST: [HOST]
          MYSQL_USER: [USER]
          MYSQL_PASS: [PASS]
          MYSQL_DB_NAME: [DB NAME]
        ports:
            - 7000:80
        volumes:
          - data:/app/instance
          - data:/app/uploads
    volumes:
        data:
   ```
   TESSERACT_DB_TYPE can be:
   * mysql
   * sqlite
   
   If using sqlite, other environment variables are not needed
2. Run the compose file
   ```sh
   docker-compose up
   ```
3. Verify connectivity


<!-- USAGE EXAMPLES -->
## Usage

To get the default admin password go to `https://[your_tesseract_instance]/newinstall`
This password can be used to log in to the `admin` account. From here you can create new users.
The newinstall page should be inaccessible after the first time `admin` logs in, so make sure you note down the password.
It is also recommended that you change the password.

More usage information TBA

<!-- LICENSE -->
## License

Distributed under the GPL-3.0 License.



<!-- CONTACT -->
## Contact

Twitter - [@willscargill](https://twitter.com/willscargill)

Project Link: [https://github.com/will-scargill/tesseract](https://github.com/will-scargill/tesseract)
