package com.eos.eapps.core.network

import io.ktor.client.*
import io.ktor.client.request.*
import io.ktor.client.statement.*

class HttpService {
    private val client = HttpClient()

    suspend fun get(url: String): String =
        client.get(url).bodyAsText()

    suspend fun post(url: String, body: String): String =
        client.post(url) { setBody(body) }.bodyAsText()

    suspend fun download(url: String): ByteArray =
        client.get(url).readBytes()

    fun close() = client.close()
}
