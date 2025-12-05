const user_redirect = fetch(
	"/users/me",
	{ method: "GET" }
).then(response => response.json())
.then(data => {
	if (data.username == undefined) {
		window.location.href = "/login";
	}
});