# CloudProject-Edge
Cloud project Edge section repository.

## Run containers locally
1. Install the `docker compose` plugin.
2. Execute:
	```bash
	docker compose up
	```

## Clean the local envroiment
Executing `./clean.sh` will stop all running containers and will delete the previously pulled images.

## Manually build and push images
1. `cd` into `images` folder.
2. Install the `docker buildx` plugin (multi-architecture build).
3. Execute `docker login` and login into your personal Docker Hub account.
4. Insert your Docker Hub username in `config.sh`.

5. Create a dockerx builder with:
	```bash
	docker buildx create --name mybuilder --use --bootstrap
	```

6. Simply run `build-and-push-all.sh`.
