const whitelistedOrigins = [
	"http://localhost",
	"http://localhost:8080",
	"http://localhost:8000",
]

const whitelistedPathRegex= /\/[^.]*$/

let token = ''

self.addEventListener('message', function(event) {
	if (event.data && event.data.type === 'SET_TOKEN') {
		token = event.data.token;
		console.log("[SW] token set!");
	}
	else {
		console.log("echo")
		console.log(event.data)
	}
})


const addAuthHeader = function(event) {
	console.log("adding auth")
	destURL = new URL(event.request.url);
	if (whitelistedOrigins.includes(destURL.origin) && whitelistedPathRegex.test(destURL.pathname)) {
		const modifiedHeaders = new Headers(event.request.heeaders);
		if (token) {
			modifiedHeaders.append('Authorization', token)
			const authReq = new Request(event.request, { headers: modifiedHeaders });
			event.respondWith((async () => fetch(authReq))());
		}
		else {
			event.respondWith((async () => fetch(event.request))())
		}
		
	}
}

self.addEventListener('fetch', addAuthHeader);

console.log("serviceworker is register")