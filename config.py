CLIENT_ID="487f4237f6484a1a85f120368cc4e63e"
CLIENT_SECRET="f376972be34a416e89a48abd05e94b15"
REDIRECT_URL="http://127.0.0.1:5000/instagram_callback"
INSTA_AUTH_URL = "https://www.instagram.com/oauth/authorize/?client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URL +"&response_type=code"
CLIENT_INSTA_AUTH_URL = "https://www.instagram.com/oauth/authorize/?client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URL +"&response_type=token"
ACCESS_TOKEN_URL="https://api.instagram.com/oauth/access_token"
INSTAGRAM_URL = "https://www.instagram.com/"
MONGODB_SETTINGS = {
	'db' : 'getevangelized'
}