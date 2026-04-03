const EOFFICE_API = "http://localhost:3001";

// ============================================================
// Homepage & Common Triggers
// ============================================================

function onHomepage(e) {
  return buildHomepageCard();
}

function onSettings(e) {
  return buildSettingsCard();
}

// ============================================================
// Google Docs Triggers
// ============================================================

function onDocsOpen(e) {
  return buildDocsCard(e);
}

function summarizeSelection(e) {
  const doc = DocumentApp.getActiveDocument();
  const selection = doc.getSelection();

  if (!selection) {
    return buildNotificationCard("No Selection", "Please select some text in your document first.");
  }

  const elements = selection.getRangeElements();
  const text = elements
    .map(function (el) {
      const element = el.getElement();
      if (element.editAsText) {
        const t = element.editAsText();
        if (el.isPartial()) {
          return t.getText().substring(el.getStartOffset(), el.getEndOffsetInclusive() + 1);
        }
        return t.getText();
      }
      return "";
    })
    .join("\n");

  if (!text.trim()) {
    return buildNotificationCard("Empty Selection", "The selected text is empty.");
  }

  const response = callEBot("Summarize the following text concisely:\n\n" + text);

  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle("eBot Summary"))
    .addSection(
      CardService.newCardSection()
        .addWidget(CardService.newTextParagraph().setText(response))
        .addWidget(
          CardService.newTextButton()
            .setText("Insert Below Selection")
            .setOnClickAction(
              CardService.newAction()
                .setFunctionName("insertTextBelowSelection")
                .setParameters({ text: response })
            )
        )
    )
    .build();
}

function insertTextBelowSelection(e) {
  const text = e.parameters.text;
  const doc = DocumentApp.getActiveDocument();
  const body = doc.getBody();
  const cursor = doc.getCursor();

  if (cursor) {
    const element = cursor.getElement();
    const parent = element.getParent();
    const index = body.getChildIndex(parent) + 1;
    body.insertParagraph(index, text);
  } else {
    body.appendParagraph(text);
  }

  return buildNotificationCard("Inserted", "eBot summary has been inserted into the document.");
}

function importToEDocs(e) {
  const doc = DocumentApp.getActiveDocument();
  const title = doc.getName();
  const body = doc.getBody().getText();

  const payload = {
    title: title,
    content: body,
    source: "google-docs",
    sourceId: doc.getId(),
    mimeType: "text/plain",
  };

  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  try {
    const response = UrlFetchApp.fetch(EOFFICE_API + "/api/edocs/import", options);
    const result = JSON.parse(response.getContentText());
    return buildNotificationCard(
      "Exported to eDocs",
      'Document "' + title + '" has been exported to eDocs.\nID: ' + (result.id || "N/A")
    );
  } catch (err) {
    return buildNotificationCard("Export Failed", "Error: " + err.message);
  }
}

// ============================================================
// Google Sheets Triggers
// ============================================================

function onSheetsOpen(e) {
  return buildSheetsCard(e);
}

function syncToESheets(e) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const rows = data.slice(1);

  const payload = {
    title: ss.getName(),
    sheetName: sheet.getName(),
    headers: headers,
    rows: rows,
    source: "google-sheets",
    sourceId: ss.getId(),
  };

  var options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  try {
    var response = UrlFetchApp.fetch(EOFFICE_API + "/api/esheets/sync", options);
    var result = JSON.parse(response.getContentText());
    return buildNotificationCard(
      "Synced to eSheets",
      "Sheet '" +
        sheet.getName() +
        "' synced successfully.\n" +
        rows.length +
        " rows, " +
        headers.length +
        " columns."
    );
  } catch (err) {
    return buildNotificationCard("Sync Failed", "Error: " + err.message);
  }
}

function pullFromESheets(e) {
  var sheetId = e.parameters.sheetId;

  try {
    var response = UrlFetchApp.fetch(EOFFICE_API + "/api/esheets/" + sheetId, {
      muteHttpExceptions: true,
    });
    var result = JSON.parse(response.getContentText());

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getActiveSheet();

    if (result.headers && result.rows) {
      sheet.clear();
      sheet.appendRow(result.headers);
      result.rows.forEach(function (row) {
        sheet.appendRow(row);
      });
    }

    return buildNotificationCard("Imported from eSheets", "Data imported successfully.");
  } catch (err) {
    return buildNotificationCard("Import Failed", "Error: " + err.message);
  }
}

// ============================================================
// Gmail Triggers
// ============================================================

function onGmailCompose(e) {
  return buildGmailComposeCard(e);
}

function getEBotSuggestion(e) {
  var context = e.parameters.context || "";
  var prompt =
    "Help me write a professional email response. Context:\n\n" + context;
  var response = callEBot(prompt);

  return CardService.newUpdateDraftActionResponseBuilder()
    .setUpdateDraftBodyAction(
      CardService.newUpdateDraftBodyAction()
        .addUpdateContent(response, CardService.ContentType.MUTABLE_HTML)
        .setUpdateType(CardService.UpdateDraftBodyType.INSERT_AT_START)
    )
    .build();
}

// ============================================================
// eBot API
// ============================================================

function callEBot(prompt) {
  var payload = {
    prompt: prompt,
    source: "google-workspace",
  };

  var options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  try {
    var response = UrlFetchApp.fetch(EOFFICE_API + "/api/ebot", options);
    var result = JSON.parse(response.getContentText());
    return result.response || result.message || "No response from eBot.";
  } catch (err) {
    return "Error connecting to eBot: " + err.message;
  }
}
