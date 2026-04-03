package org.embeddedos.eoffice

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.command.WriteCommandAction
import com.intellij.openapi.progress.ProgressIndicator
import com.intellij.openapi.progress.ProgressManager
import com.intellij.openapi.progress.Task
import com.intellij.openapi.ui.Messages

class EBotAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val selectionModel = editor.selectionModel
        val selectedText = selectionModel.selectedText

        if (selectedText.isNullOrBlank()) {
            Messages.showWarningDialog(project, "No text selected.", "eBot")
            return
        }

        val prompt = "Summarize the following text concisely:\n\n$selectedText"

        ProgressManager.getInstance().run(object : Task.Backgroundable(project, "eBot: Summarizing...", true) {
            override fun run(indicator: ProgressIndicator) {
                indicator.isIndeterminate = true
                val svc = EOfficeService.getInstance(project)
                val result = svc.ebotChat(prompt)

                ApplicationManager.getApplication().invokeLater {
                    val choice = Messages.showDialog(
                        project,
                        result,
                        "🤖 eBot Summary",
                        arrayOf("Replace Selection", "Copy to Clipboard", "Cancel"),
                        0,
                        Messages.getInformationIcon()
                    )

                    when (choice) {
                        0 -> {
                            WriteCommandAction.runWriteCommandAction(project) {
                                editor.document.replaceString(
                                    selectionModel.selectionStart,
                                    selectionModel.selectionEnd,
                                    result
                                )
                            }
                        }
                        1 -> {
                            val clipboard = java.awt.Toolkit.getDefaultToolkit().systemClipboard
                            clipboard.setContents(java.awt.datatransfer.StringSelection(result), null)
                        }
                    }
                }
            }
        })
    }

    override fun update(e: AnActionEvent) {
        val editor = e.getData(CommonDataKeys.EDITOR)
        e.presentation.isEnabledAndVisible = editor != null && editor.selectionModel.hasSelection()
    }
}

class EBotRewriteAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        val project = e.project ?: return
        val editor = e.getData(CommonDataKeys.EDITOR) ?: return
        val selectionModel = editor.selectionModel
        val selectedText = selectionModel.selectedText

        if (selectedText.isNullOrBlank()) {
            Messages.showWarningDialog(project, "No text selected.", "eBot")
            return
        }

        val prompt = "Rewrite the following text to be clearer and more professional:\n\n$selectedText"

        ProgressManager.getInstance().run(object : Task.Backgroundable(project, "eBot: Rewriting...", true) {
            override fun run(indicator: ProgressIndicator) {
                indicator.isIndeterminate = true
                val svc = EOfficeService.getInstance(project)
                val result = svc.ebotChat(prompt)

                ApplicationManager.getApplication().invokeLater {
                    val choice = Messages.showDialog(
                        project,
                        result,
                        "🤖 eBot Rewrite",
                        arrayOf("Replace Selection", "Copy to Clipboard", "Cancel"),
                        0,
                        Messages.getInformationIcon()
                    )

                    when (choice) {
                        0 -> {
                            WriteCommandAction.runWriteCommandAction(project) {
                                editor.document.replaceString(
                                    selectionModel.selectionStart,
                                    selectionModel.selectionEnd,
                                    result
                                )
                            }
                        }
                        1 -> {
                            val clipboard = java.awt.Toolkit.getDefaultToolkit().systemClipboard
                            clipboard.setContents(java.awt.datatransfer.StringSelection(result), null)
                        }
                    }
                }
            }
        })
    }

    override fun update(e: AnActionEvent) {
        val editor = e.getData(CommonDataKeys.EDITOR)
        e.presentation.isEnabledAndVisible = editor != null && editor.selectionModel.hasSelection()
    }
}
