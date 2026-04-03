// ============================================================
// Card UI Builder Functions for eOffice Google Workspace Add-on
// ============================================================

function buildHomepageCard() {
  var header = CardService.newCardHeader()
    .setTitle("eOffice")
    .setSubtitle("Your AI-powered office suite");

  var appsSection = CardService.newCardSection().setHeader("📱 Apps");

  var apps = [
    { name: "eDocs", icon: "DESCRIPTION", path: "edocs" },
    { name: "eNotes", icon: "BOOKMARK", path: "enotes" },
    { name: "eSheets", icon: "EVENT_SEAT", path: "esheets" },
    { name: "eSlides", icon: "VIDEO_PLAY", path: "eslides" },
    { name: "eMail", icon: "EMAIL", path: "email" },
    { name: "eDrive", icon: "CLOUD", path: "edrive" },
    { name: "eConnect", icon: "CHAT", path: "econnect" },
    { name: "eForms", icon: "FEEDBACK", path: "eforms" },
    { name: "ePlanner", icon: "INVITE", path: "eplanner" },
  ];

  apps.forEach(function (app) {
    appsSection.addWidget(
      CardService.newDecoratedText()
        .setText(app.name)
        .setStartIcon(
          CardService.newIconImage().setIcon(CardService.Icon[app.icon])
        )
        .setOnClickAction(
          CardService.newAction()
            .setFunctionName("openApp")
            .setParameters({ app: app.path })
        )
    );
  });

  var ebotSection = CardService.newCardSection()
    .setHeader("🤖 eBot AI")
    .addWidget(
      CardService.newTextInput()
        .setFieldName("ebotQuery")
        .setTitle("Ask eBot anything...")
        .setMultiline(true)
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Ask eBot")
        .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
        .setBackgroundColor("#4f46e5")
        .setOnClickAction(
          CardService.newAction().setFunctionName("askEBotFromHomepage")
        )
    );

  return CardService.newCardBuilder()
    .setHeader(header)
    .addSection(ebotSection)
    .addSection(appsSection)
    .build();
}

function buildDocsCard(e) {
  var header = CardService.newCardHeader()
    .setTitle("eOffice for Docs")
    .setSubtitle("AI writing assistant & document tools");

  var aiSection = CardService.newCardSection()
    .setHeader("🤖 eBot AI")
    .addWidget(
      CardService.newTextButton()
        .setText("📝 Summarize Selection")
        .setOnClickAction(
          CardService.newAction().setFunctionName("summarizeSelection")
        )
    )
    .addWidget(
      CardService.newTextButton()
        .setText("✍️ Rewrite Selection")
        .setOnClickAction(
          CardService.newAction()
            .setFunctionName("rewriteSelection")
        )
    )
    .addWidget(
      CardService.newTextInput()
        .setFieldName("ebotQuery")
        .setTitle("Ask eBot about this document...")
        .setMultiline(true)
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Ask eBot")
        .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
        .setBackgroundColor("#4f46e5")
        .setOnClickAction(
          CardService.newAction().setFunctionName("askEBotFromDocs")
        )
    );

  var exportSection = CardService.newCardSection()
    .setHeader("📤 Export")
    .addWidget(
      CardService.newTextButton()
        .setText("Export to eDocs")
        .setOnClickAction(
          CardService.newAction().setFunctionName("importToEDocs")
        )
    );

  return CardService.newCardBuilder()
    .setHeader(header)
    .addSection(aiSection)
    .addSection(exportSection)
    .build();
}

function buildSheetsCard(e) {
  var header = CardService.newCardHeader()
    .setTitle("eOffice for Sheets")
    .setSubtitle("Sync spreadsheets with eSheets");

  var syncSection = CardService.newCardSection()
    .setHeader("🔄 Sync")
    .addWidget(
      CardService.newTextButton()
        .setText("Push to eSheets")
        .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
        .setBackgroundColor("#4f46e5")
        .setOnClickAction(
          CardService.newAction().setFunctionName("syncToESheets")
        )
    )
    .addWidget(
      CardService.newTextInput()
        .setFieldName("esheetId")
        .setTitle("eSheets ID (to pull)")
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Pull from eSheets")
        .setOnClickAction(
          CardService.newAction().setFunctionName("pullFromESheetsAction")
        )
    );

  var aiSection = CardService.newCardSection()
    .setHeader("🤖 eBot AI")
    .addWidget(
      CardService.newTextInput()
        .setFieldName("ebotQuery")
        .setTitle("Ask eBot about this sheet...")
        .setMultiline(true)
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Ask eBot")
        .setOnClickAction(
          CardService.newAction().setFunctionName("askEBotFromSheets")
        )
    );

  return CardService.newCardBuilder()
    .setHeader(header)
    .addSection(syncSection)
    .addSection(aiSection)
    .build();
}

function buildGmailComposeCard(e) {
  var header = CardService.newCardHeader()
    .setTitle("eBot Compose Helper")
    .setSubtitle("AI-powered email drafting");

  var section = CardService.newCardSection()
    .addWidget(
      CardService.newTextInput()
        .setFieldName("emailContext")
        .setTitle("What should the email be about?")
        .setMultiline(true)
    )
    .addWidget(
      CardService.newSelectionInput()
        .setFieldName("emailTone")
        .setTitle("Tone")
        .setType(CardService.SelectionInputType.DROPDOWN)
        .addItem("Professional", "professional", true)
        .addItem("Friendly", "friendly", false)
        .addItem("Formal", "formal", false)
        .addItem("Concise", "concise", false)
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Generate with eBot")
        .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
        .setBackgroundColor("#4f46e5")
        .setOnClickAction(
          CardService.newAction().setFunctionName("generateEmailDraft")
        )
    );

  return CardService.newCardBuilder()
    .setHeader(header)
    .addSection(section)
    .build();
}

function buildSettingsCard() {
  var header = CardService.newCardHeader().setTitle("eOffice Settings");

  var section = CardService.newCardSection()
    .addWidget(
      CardService.newTextInput()
        .setFieldName("backendUrl")
        .setTitle("Backend URL")
        .setValue("http://localhost:3001")
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Save Settings")
        .setOnClickAction(
          CardService.newAction().setFunctionName("saveSettings")
        )
    )
    .addWidget(
      CardService.newTextButton()
        .setText("Test Connection")
        .setOnClickAction(
          CardService.newAction().setFunctionName("testConnection")
        )
    );

  return CardService.newCardBuilder()
    .setHeader(header)
    .addSection(section)
    .build();
}

function buildNotificationCard(title, message) {
  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle(title))
    .addSection(
      CardService.newCardSection().addWidget(
        CardService.newTextParagraph().setText(message)
      )
    )
    .build();
}

// ============================================================
// Action Handlers
// ============================================================

function openApp(e) {
  var app = e.parameters.app;
  return CardService.newActionResponseBuilder()
    .setOpenLink(
      CardService.newOpenLink()
        .setUrl("http://localhost:3001/apps/" + app)
        .setOpenAs(CardService.OpenAs.FULL_SIZE)
    )
    .build();
}

function askEBotFromHomepage(e) {
  var query = e.formInput.ebotQuery;
  if (!query) {
    return buildNotificationCard("eBot", "Please enter a question.");
  }
  var response = callEBot(query);
  return buildNotificationCard("eBot", response);
}

function askEBotFromDocs(e) {
  var query = e.formInput.ebotQuery;
  var doc = DocumentApp.getActiveDocument();
  var context = doc ? doc.getBody().getText().substring(0, 2000) : "";
  var prompt = query + "\n\nDocument context:\n" + context;
  var response = callEBot(prompt);
  return buildNotificationCard("eBot", response);
}

function askEBotFromSheets(e) {
  var query = e.formInput.ebotQuery;
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var preview = data.slice(0, 10).map(function (r) { return r.join(", "); }).join("\n");
  var prompt = query + "\n\nSheet preview:\n" + preview;
  var response = callEBot(prompt);
  return buildNotificationCard("eBot", response);
}

function rewriteSelection(e) {
  var doc = DocumentApp.getActiveDocument();
  var selection = doc.getSelection();
  if (!selection) {
    return buildNotificationCard("No Selection", "Please select some text.");
  }
  var elements = selection.getRangeElements();
  var text = elements.map(function (el) {
    return el.getElement().editAsText ? el.getElement().editAsText().getText() : "";
  }).join("\n");
  var response = callEBot("Rewrite this text to be clearer and more professional:\n\n" + text);
  return buildNotificationCard("eBot Rewrite", response);
}

function generateEmailDraft(e) {
  var context = e.formInput.emailContext || "";
  var tone = e.formInput.emailTone || "professional";
  var prompt = "Write a " + tone + " email about: " + context;
  var response = callEBot(prompt);

  return CardService.newUpdateDraftActionResponseBuilder()
    .setUpdateDraftBodyAction(
      CardService.newUpdateDraftBodyAction()
        .addUpdateContent(response, CardService.ContentType.MUTABLE_HTML)
        .setUpdateType(CardService.UpdateDraftBodyType.INSERT_AT_START)
    )
    .build();
}

function pullFromESheetsAction(e) {
  var sheetId = e.formInput.esheetId;
  if (!sheetId) {
    return buildNotificationCard("Missing ID", "Please enter an eSheets ID.");
  }
  return pullFromESheets({ parameters: { sheetId: sheetId } });
}

function saveSettings(e) {
  var url = e.formInput.backendUrl || "http://localhost:3001";
  PropertiesService.getUserProperties().setProperty("EOFFICE_API", url);
  return buildNotificationCard("Settings Saved", "Backend URL set to: " + url);
}

function testConnection(e) {
  try {
    var url = PropertiesService.getUserProperties().getProperty("EOFFICE_API") || "http://localhost:3001";
    var response = UrlFetchApp.fetch(url + "/api/health", { muteHttpExceptions: true });
    return buildNotificationCard("Connection Test", "Status: " + response.getResponseCode());
  } catch (err) {
    return buildNotificationCard("Connection Failed", "Error: " + err.message);
  }
}
