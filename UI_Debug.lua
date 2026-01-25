local debugFrame = CreateFrame("Frame", "UunaDebugFrame", UIParent, "BasicFrameTemplateWithInset");
debugFrame:SetSize(350, 220);
debugFrame:SetPoint("TOP", UIParent, "BOTTOM", 0, -500);
debugFrame:Hide();
debugFrame.title = debugFrame:CreateFontString(nil, "OVERLAY", "GameFontHighlight");
debugFrame.title:SetPoint("CENTER", debugFrame.TitleBg, "CENTER", 0, 0);
debugFrame.title:SetText("Technical Debug Log");
local text = debugFrame:CreateFontString(nil, "OVERLAY", "GameFontNormal");
text:SetPoint("TOPLEFT", 15, -40);
text:SetPoint("BOTTOMRIGHT", -15, 60);
text:SetJustifyH("LEFT");
text:SetJustifyV("TOP");
text:SetText("Waiting for events...");
local pageText = debugFrame:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall");
pageText:SetPoint("BOTTOM", 0, 45);
pageText:SetText("0 / 0");
function UunaAddon:UpdateDebugUI()
	local total = #UunaDebugHistory;
	if total > 0 then
		UunaAddon.currentDebugIndex = math.min(UunaAddon.currentDebugIndex, total);
		text:SetText(UunaDebugHistory[UunaAddon.currentDebugIndex]);
		pageText:SetText(UunaAddon.currentDebugIndex .. " / " .. total);
	else
		text:SetText("No events captured yet.");
		pageText:SetText("0 / 0");
	end;
end;
local function CreateNavBtn(parent, point, label, delta)
	local btn = CreateFrame("Button", nil, parent, "GameMenuButtonTemplate");
	btn:SetSize(40, 25);
	btn:SetPoint(point, parent, point, point == "BOTTOMLEFT" and 20 or (-20), 10);
	btn:SetText(label);
	btn:SetScript("OnClick", function()
		local newIndex = UunaAddon.currentDebugIndex + delta;
		if newIndex >= 1 and newIndex <= (#UunaDebugHistory) then
			UunaAddon.currentDebugIndex = newIndex;
			UunaAddon:UpdateDebugUI();
		end;
	end);
	return btn;
end;
local prevBtn = CreateNavBtn(debugFrame, "BOTTOMLEFT", "<", -1);
local nextBtn = CreateNavBtn(debugFrame, "BOTTOMRIGHT", ">", 1);
function UunaAddon:ToggleDebug()
	if debugFrame:IsShown() then
		debugFrame:Hide();
	else
		if UunaLogFrame then
			debugFrame:ClearAllPoints();
			debugFrame:SetPoint("TOP", UunaLogFrame, "BOTTOM", 0, -5);
		end;
		self:UpdateDebugUI();
		debugFrame:Show();
	end;
end;
