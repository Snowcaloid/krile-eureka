# Snowcaloid Discord bot

Created using Python.

## Requirements

Install docker on your machine.

After installing docker, you need to set up a couple of variables - for this, you need to create a `.env` file with the approperiate variables from `.env.example`.

Additionally, the `docker-compose.yaml` needs to be adjusted depending on whether or not you're using [portainer](https://www.portainer.io/) to run the repository.

### Portainer

* Deploy a stack: https://www.portainer.io/blog/stacks-docker-compose-the-portainer-way
* Choose repository
* Use github auth token (if necessery) to be able to clone the repository
* Add all variables to the custom environment variables from [.env.example](.env.example)
* Start the stack

### Traditional way

* Clone the repository
* `cp .env.example .env`
* Set all the variables in .env.example
* Adjust `docker-compose.yml`:
  * The following line is required in every service:
  ```
  env_file:
  - .env
  ```
* To start the production version, run `docker-compose up --build -d`

### Debugging with VS Code

* Install Docker extensions and debugpy
* Follow the traditional way, but use `docker-compose-debug.yml`
* Set the WAIT_DEBUG Variable to true
* F5 (Run Debugger)

### Common issues

* Make sure that the paths in `docker-compose.yml` are compatible with the system you're running the bot on.
* When using github codespaces, you might have to run the program with debugger twice for it to start debugging properly.