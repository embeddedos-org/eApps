package org.embeddedos.eoffice

import com.intellij.ide.BrowserUtil
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.components.Service
import com.intellij.openapi.components.service
import com.intellij.openapi.project.Project
import com.google.gson.Gson
import com.google.gson.JsonObject
import java.net.HttpURLConnection
import java.net.URL

@Service(Service.Level.PROJECT)
class EOfficeService(private val project: Project) {
    var ebotHost: String = "localhost"
    var ebotPort: Int = 3001

    val baseUrl: String get() = "http://$ebotHost:$ebotPort"

    fun ebotChat(message: String): String {
        return try {
            val url = URL("$baseUrl/api/ebot/chat")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json")
            conn.doOutput = true
            conn.connectTimeout = 5000
            conn.readTimeout = 30000

            val body = Gson().toJson(mapOf("message" to message))
            conn.outputStream.use { it.write(body.toByteArray()) }

            if (conn.responseCode == 200) {
                val response = conn.inputStream.bufferedReader().readText()
                val json = Gson().fromJson(response, JsonObject::class.java)
                json.get("text")?.asString
                    ?: json.get("response")?.asString
                    ?: "No response from eBot."
            } else {
                "eBot returned HTTP ${conn.responseCode}"
            }
        } catch (e: Exception) {
            "eBot is offline. Start the eOffice server. (${e.message})"
        }
    }

    companion object {
        fun getInstance(project: Project): EOfficeService = project.service()
    }
}

class OpenEDocsAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val svc = EOfficeService.getInstance(project)
        BrowserUtil.browse("${svc.baseUrl}/edocs")
    }
}

class OpenENotesAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val svc = EOfficeService.getInstance(project)
        BrowserUtil.browse("${svc.baseUrl}/enotes")
    }
}

class OpenESheetsAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val svc = EOfficeService.getInstance(project)
        BrowserUtil.browse("${svc.baseUrl}/esheets")
    }
}

class EBotChatAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val svc = EOfficeService.getInstance(project)
        BrowserUtil.browse("${svc.baseUrl}/ebot")
    }
}
