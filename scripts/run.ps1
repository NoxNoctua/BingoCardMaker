Param(
    $Command
)
If (-Not $Command -eq '') {
    docker run --rm --name devtest --mount type=bind,source=$(pwd),target=/app --volume /app/.venv --publish 8000:8000 -it $(docker build -q .) "$Command"
} Else {
    docker run --rm --name devtest --mount type=bind,source=$(pwd),target=/app --volume /app/.venv --publish 8000:8000 -it $(docker build -q .)  "./src/devscripts/start.sh"
}
