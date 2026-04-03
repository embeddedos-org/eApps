package org.embeddedos.eoffice

import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.content.ContentFactory
import com.intellij.ui.components.JBList
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextField
import com.intellij.ide.BrowserUtil
import java.awt.BorderLayout
import java.awt.Dimension
import java.awt.FlowLayout
import javax.swing.*

class EOfficeToolWindowFactory : ToolWindowFactory {
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val contentFactory = ContentFactory.getInstance()

        // Apps Tab
        val appsPanel = createAppsPanel(project)
        val appsContent = contentFactory.createContent(appsPanel, "Apps", false)
        toolWindow.contentManager.addContent(appsContent)

        // Recent Files Tab
        val recentPanel = createRecentPanel()
        val recentContent = contentFactory.createContent(recentPanel, "Recent Files", false)
        toolWindow.contentManager.addContent(recentContent)

        // eBot Tab
        val ebotPanel = createEBotPanel(project)
        val ebotContent = contentFactory.createContent(ebotPanel, "eBot", false)
        toolWindow.contentManager.addContent(ebotContent)
    }

    private fun createAppsPanel(project: Project): JPanel {
        val panel = JPanel(BorderLayout())
        val svc = EOfficeService.getInstance(project)

        data class AppItem(val icon: String, val name: String, val path: String)
        val apps = listOf(
            AppItem("📝", "eDocs", "edocs"),
            AppItem("📒", "eNotes", "enotes"),
            AppItem("📊", "eSheets", "esheets"),
            AppItem("📽️", "eSlides", "eslides"),
            AppItem("✉️", "eMail", "email"),
            AppItem("☁️", "eDrive", "edrive"),
            AppItem("💬", "eConnect", "econnect"),
            AppItem("📋", "eForms", "eforms"),
            AppItem("📅", "ePlanner", "eplanner"),
        )

        val listModel = DefaultListModel<String>()
        apps.forEach { listModel.addElement("${it.icon}  ${it.name}") }

        val list = JBList(listModel)
        list.selectionMode = ListSelectionModel.SINGLE_SELECTION
        list.fixedCellHeight = 32
        list.addListSelectionListener {
            if (!it.valueIsAdjusting) {
                val idx = list.selectedIndex
                if (idx >= 0) {
                    BrowserUtil.browse("${svc.baseUrl}/${apps[idx].path}")
                    list.clearSelection()
                }
            }
        }

        panel.add(JBScrollPane(list), BorderLayout.CENTER)
        return panel
    }

    private fun createRecentPanel(): JPanel {
        val panel = JPanel(BorderLayout())

        val listModel = DefaultListModel<String>()
        listModel.addElement("No recent files")

        val list = JBList(listModel)
        list.selectionMode = ListSelectionModel.SINGLE_SELECTION
        list.fixedCellHeight = 28

        panel.add(JBScrollPane(list), BorderLayout.CENTER)
        return panel
    }

    private fun createEBotPanel(project: Project): JPanel {
        val panel = JPanel(BorderLayout())

        val chatArea = JTextArea()
        chatArea.isEditable = false
        chatArea.lineWrap = true
        chatArea.wrapStyleWord = true
        chatArea.append("🤖 eBot AI Assistant\n")
        chatArea.append("Ask me anything or paste text to summarize.\n\n")

        val scrollPane = JBScrollPane(chatArea)
        panel.add(scrollPane, BorderLayout.CENTER)

        val inputPanel = JPanel(BorderLayout())
        val inputField = JBTextField()
        inputField.emptyText.setText("Type a message...")

        val sendButton = JButton("Send")
        sendButton.preferredSize = Dimension(80, 30)

        val sendMessage = {
            val text = inputField.text.trim()
            if (text.isNotEmpty()) {
                chatArea.append("You: $text\n\n")
                inputField.text = ""

                SwingWorker.execute {
                    val svc = EOfficeService.getInstance(project)
                    val response = svc.ebotChat(text)
                    SwingUtilities.invokeLater {
                        chatArea.append("🤖 eBot: $response\n\n")
                        chatArea.caretPosition = chatArea.document.length
                    }
                }
            }
        }

        sendButton.addActionListener { sendMessage() }
        inputField.addActionListener { sendMessage() }

        inputPanel.add(inputField, BorderLayout.CENTER)
        inputPanel.add(sendButton, BorderLayout.EAST)
        panel.add(inputPanel, BorderLayout.SOUTH)

        return panel
    }
}

private object SwingWorker {
    fun execute(task: () -> Unit) {
        Thread(task).apply {
            isDaemon = true
            start()
        }
    }
}
