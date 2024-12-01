## 使用说明
样板的 applelogin.py 文件原为 `lanqian528/chat2api` 编写，添加两个路由 `/auth/url`、`/auth/session`，用以对接浏览器插件。

其中 `/auth/url` 需要在被 `GET` 请求时以 JSON 形式返回三个值 `u`、`d`、`v`。其中 `u` 是客户端登录 OpenAI 账号使用的链接，`d` 是访问这个链接所需要使用的 Cookie 的值，而 `v` 是拼接链接时生成 `code_challenge` 所使用的 `code_verifier` 的值。

另外的 `/auth/session` 接口则用于接收客户端 `POST` 发送的数据。客户端需要以 JSON 形式向此接口发送两个值 `location`、`codeVerifier`。其中 `location` 是客户端最后 302 重定向时的地址 —— iOS 客户端的回调 `callback` 链接，`codeVerifier` 为此前服务端发送给客户端的 `v` 的值。服务端需要使用这两项数据请求获取 `refresh_token` 以及 `access_token`，并将数据返回客户端。