# CloudProject-Edge
Cloud project Edge section repository.

## Run containers locally
1. Install the `docker compose` plugin.
2. Execute:
	```
	docker compose up
	```

3. View logs:
	```
	docker compose logs [ hash-saver | hasher | outliet-detector ]
	```

4. Stop containers:
	```
	docker compose kill
	docker compose rm -f
	```

5. Clean the envroiment: just run `clean.sh`; executing that script will stop all running containers and will delete the previously pulled images.

## Manually build and push images
1. `cd` into `images` folder.
2. Install the `docker buildx` plugin (multi-architecture build).
3. Execute `docker login` and login into your personal Docker Hub account.
4. Insert your Docker Hub username in `config.sh`.
5. Create a dockerx builder with:
	```
	docker buildx create --name mybuilder --use --bootstrap
	```
6. Simply run `build-and-push-all.sh`.

## Local Database (text) file
You will find a local copy of the blocks'hashes inside the [data](data) folder.
