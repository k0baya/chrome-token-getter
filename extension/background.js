chrome.action.onClicked.addListener(async function (tab) {
    chrome.storage.local.get('remoteurl', async function(result) {
        if (result.remoteurl) {
            const fullUrl = result.remoteurl.endsWith('/') ? `${result.remoteurl}auth/url` : `${result.remoteurl}/auth/url`; // Append 'gptlogin'
            try {
                const response = await fetch(fullUrl);
                const data = await response.json();
                const loginurl = data.u; // Extract 'u' as loginurl
                const auth0Value = data.d; // Extract 'd' as auth0 cookie value
                const codeVerifier = data.v; // Extract 'v' as codeVerifier

                if (loginurl && auth0Value && codeVerifier) {
                    // Set the 'auth0' cookie before opening the loginurl
                    await chrome.cookies.set({
                        url: "https://auth0.openai.com",
                        name: "auth0",
                        value: auth0Value,
                        path: "/",
                        secure: true,
                        httpOnly: true
                    });

                    chrome.storage.local.set({ loginurl: loginurl, codeVerifier: codeVerifier }, function () {
                        chrome.tabs.create({ url: loginurl });
                    });
                } else {
                    throw new Error('未能获取登录链接或相关数据');
                }
            } catch (error) {
                console.log(error);
                chrome.storage.local.set({ error: error }, function () {
                    chrome.tabs.create({ url: 'error.html' });
                });
            }
        } else {
            chrome.tabs.create({ url: 'settings.html' });
        }
    });
});

chrome.webRequest.onBeforeRedirect.addListener(
    function (details) {
        console.log(details);
        // code from https://github.com/wozulong/ChatGPTAuthHelper
        if (details.redirectUrl.startsWith('com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback?')) {
            const code = new URL(details.redirectUrl).searchParams.get('code');
            console.log(code);
            chrome.storage.local.set({location: details.redirectUrl}, function () {
                chrome.tabs.update(details.tabId, {url: 'popup.html'});
            });
            return {cancel: true};
        }
    },
    {urls: ["<all_urls>"]},
    ["responseHeaders"]
);