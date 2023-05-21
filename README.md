# CloudProject-Edge
Cloud project Edge section repository.

## Run containers locally
1. Install the `docker compose` plugin.
2. Start containers:
	```bash
	docker compose up -d
	```

3. View logs:
	```bash
	docker compose logs [ hash-saver | hasher | outliet-detector ]
	```

4. Stop containers:
	```bash
	docker compose kill
	```

5. Clean the envroiment:
	```bash
	docker compose rm -f
	```

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
