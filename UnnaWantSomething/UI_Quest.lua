UunaCustomQuests = UunaCustomQuests or {};
local function CreateQuestDetailModal(questID)
	local modal = CreateFrame("Frame", "UunaQuestDetailModal", UIParent, "BasicFrameTemplateWithInset");
	modal:SetSize(300, 200);
	modal:SetPoint("CENTER", UIParent, "CENTER", 20, 20);
	modal:SetFrameLevel(100);
	modal:EnableMouse(true);
	modal:SetMovable(true);
	modal:RegisterForDrag("LeftButton");
	modal:SetScript("OnDragStart", modal.StartMoving);
	modal:SetScript("OnDragStop", modal.StopMovingOrSizing);
	modal.title = modal:CreateFontString(nil, "OVERLAY", "GameFontHighlight");
	modal.title:SetPoint("CENTER", modal.TitleBg, "CENTER", 0, 0);
	modal.title:SetText("Details: Quest " .. questID);
	local infoText = modal:CreateFontString(nil, "OVERLAY", "GameFontNormal");
	infoText:SetPoint("TOPLEFT", 15, -40);
	infoText:SetJustifyH("LEFT");
	local isCompleted = C_QuestLog.IsQuestFlaggedCompleted(questID);
	local title = C_QuestLog.GetTitleForQuestID(questID) or "Unknown/Hidden";
	infoText:SetText(string.format("ID: %d\nTitle: %s\n\nStatus: %s", questID, title, isCompleted and "|cff00ff00Completed|r" or "|cffff0000Not Completed|r"));
	local close = CreateFrame("Button", nil, modal, "GameMenuButtonTemplate");
	close:SetSize(80, 25);
	close:SetPoint("BOTTOM", 0, 15);
	close:SetText("Close");
	close:SetScript("OnClick", function()
		modal:Hide();
	end);
end;
function UunaAddon:RefreshQuestList()
	local container = UunaAddon.QuestScrollChild;
	local children = {
		container:GetChildren()
	};
	for _, child in ipairs(children) do
		child:Hide();
		child:SetParent(nil);
	end;
	local y = 0;
	for i, qID in ipairs(UunaCustomQuests) do
		local line = CreateFrame("Button", nil, container);
		line:SetSize(260, 25);
		line:SetPoint("TOPLEFT", 0, y);
		local isCompleted = C_QuestLog.IsQuestFlaggedCompleted(qID);
		local statusColor = isCompleted and "|cff00ff00[DONE]|r " or "|cffff0000[OPEN]|r ";
		local text = line:CreateFontString(nil, "OVERLAY", "GameFontNormal");
		text:SetPoint("LEFT", 5, 0);
		text:SetText(statusColor .. "Quest ID: " .. qID);
		local del = CreateFrame("Button", nil, line, "UIPanelCloseButton");
		del:SetSize(20, 20);
		del:SetPoint("RIGHT", -5, 0);
		del:SetScript("OnClick", function()
			table.remove(UunaCustomQuests, i);
			UunaAddon:RefreshQuestList();
		end);
		line:SetScript("OnClick", function()
			CreateQuestDetailModal(qID);
		end);
		y = y - 25;
	end;
end;
function UunaAddon:ToggleQuestTracker()
	if not UunaQuestFrame then
		local f = CreateFrame("Frame", "UunaQuestFrame", UIParent, "BasicFrameTemplateWithInset");
		f:SetSize(300, 400);
		f:SetPoint("RIGHT", UunaLogFrame, "LEFT", -10, 0);
		f.title = f:CreateFontString(nil, "OVERLAY", "GameFontHighlight");
		f.title:SetPoint("CENTER", f.TitleBg, "CENTER", 0, 0);
		f.title:SetText("Quest Flag Tracker");
		local editBox = CreateFrame("EditBox", nil, f, "InputBoxTemplate");
		editBox:SetSize(150, 20);
		editBox:SetPoint("TOPLEFT", 20, -40);
		editBox:SetAutoFocus(false);
		editBox:SetNumeric(true);
		local addBtn = CreateFrame("Button", nil, f, "GameMenuButtonTemplate");
		addBtn:SetSize(80, 20);
		addBtn:SetPoint("LEFT", editBox, "RIGHT", 10, 0);
		addBtn:SetText("Add ID");
		addBtn:SetScript("OnClick", function()
			local id = tonumber(editBox:GetText());
			if id then
				table.insert(UunaCustomQuests, id);
				editBox:SetText("");
				UunaAddon:RefreshQuestList();
			end;
		end);
		local scroll = CreateFrame("ScrollFrame", nil, f, "UIPanelScrollFrameTemplate");
		scroll:SetPoint("TOPLEFT", 10, -70);
		scroll:SetPoint("BOTTOMRIGHT", -30, 10);
		local child = CreateFrame("Frame", nil, scroll);
		child:SetSize(260, 1);
		scroll:SetScrollChild(child);
		UunaAddon.QuestScrollChild = child;
		UunaQuestFrame = f;
	end;
	if UunaQuestFrame:IsShown() then
		UunaQuestFrame:Hide();
	else
		UunaQuestFrame:Show();
		UunaAddon:RefreshQuestList();
	end;
end;
