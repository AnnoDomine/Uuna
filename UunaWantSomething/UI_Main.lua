function UunaAddon:InitUI()
	local frame = CreateFrame("Frame", "UunaLogFrame", UIParent, "BasicFrameTemplateWithInset");
	frame:SetSize(380, 450);
	frame:SetPoint("CENTER");
	frame:SetMovable(true);
	frame:EnableMouse(true);
	frame:RegisterForDrag("LeftButton");
	frame:SetScript("OnDragStart", frame.StartMoving);
	frame:SetScript("OnDragStop", frame.StopMovingOrSizing);
	frame:Hide();
	UunaAddon.MainFrame = frame;
	frame.title = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlight");
	frame.title:SetPoint("LEFT", frame.TitleBg, "LEFT", 10, 0);
	frame.title:SetText("Uuna Story Log");
	local closeBtn = CreateFrame("Button", nil, frame, "UIPanelCloseButton");
	closeBtn:SetPoint("TOPRIGHT", 0, -1);
	closeBtn:SetScript("OnClick", function()
		frame:Hide();
		if UunaDebugFrame then
			UunaDebugFrame:Hide();
		end;
		if UunaAuraFrame then
			UunaAuraFrame:Hide();
		end;
	end);
	local scroll = CreateFrame("ScrollFrame", "UunaStoryScrollFrame", frame, "UIPanelScrollFrameTemplate");
	scroll:SetPoint("TOPLEFT", 10, -35);
	scroll:SetPoint("BOTTOMRIGHT", -30, 40);
	local edit = CreateFrame("EditBox", nil, scroll);
	edit:SetMultiLine(true);
	edit:SetFontObject("ChatFontNormal");
	edit:SetWidth(320);
	edit:SetAutoFocus(false);
	edit:SetEnabled(true);
	scroll:SetScrollChild(edit);
	UunaAddon.StoryEditBox = edit;
	local function ScrollToBottom()
		C_Timer.After(0.1, function()
			scroll:SetVerticalScroll(scroll:GetVerticalScrollRange());
		end);
	end;
	local fullText = "";
	if UunaLogHistory then
		for _, line in ipairs(UunaLogHistory) do
			fullText = fullText .. line .. "\n";
		end;
	end;
	edit:SetText(fullText);
	ScrollToBottom();
	function UunaAddon:UpdateStoryUI(newLine)
		local safeLine = tostring(newLine or "");
		local currentText = tostring(UunaAddon.StoryEditBox:GetText() or "");
		local cleanNewText = currentText .. safeLine .. "\n";
		UunaAddon.StoryEditBox:SetText(cleanNewText);
		ScrollToBottom();
	end;
	local menuFrame = CreateFrame("Frame", "UunaMenuFrame", UIParent, "UIDropDownMenuTemplate");
	local optBtn = CreateFrame("Button", nil, frame, "GameMenuButtonTemplate");
	optBtn:SetSize(80, 20);
	optBtn:SetPoint("BOTTOM", 0, 10);
	optBtn:SetText("Options");
	optBtn:SetScript("OnClick", function(self)
		UIDropDownMenu_Initialize(menuFrame, function(self, level)
			local info = UIDropDownMenu_CreateInfo();
			info.text = "Uuna Management";
			info.isTitle = true;
			info.notCheckable = true;
			UIDropDownMenu_AddButton(info);
			info = UIDropDownMenu_CreateInfo();
			info.text = "Summon Uuna";
			info.notCheckable = true;
			info.func = function()
				for i = 1, C_PetJournal.GetNumPets() do
					local pID, sID, owned = C_PetJournal.GetPetInfoByIndex(i);
					if owned and sID == UunaAddon.SPECIES_ID then
						C_PetJournal.SummonPetByGUID(pID);
						return;
					end;
				end;
				print("|cffffd100UunaAddon:|r Uuna (ID " .. UunaAddon.SPECIES_ID .. ") not found in collection.");
			end;
			UIDropDownMenu_AddButton(info);
			info.text = "List Auras";
			info.func = function()
				UunaAddon:ToggleAura();
			end;
			UIDropDownMenu_AddButton(info);
			info.text = "Debug Log";
			info.func = function()
				UunaAddon:ToggleDebug();
			end;
			UIDropDownMenu_AddButton(info);
			info.text = "Quest Tracker";
			info.func = function()
				UunaAddon:ToggleQuestTracker();
			end;
			UIDropDownMenu_AddButton(info);
			info.text = "|cffff0000Clear Story Log|r";
			info.func = function()
				UunaLogHistory = {};
				UunaAddon.StoryEditBox:SetText("");
				print("|cffffd100UunaAddon:|r Story Log cleared.");
				PlaySound(812);
			end;
			UIDropDownMenu_AddButton(info);
		end, "MENU");
		ToggleDropDownMenu(1, nil, menuFrame, self, 0, 0);
	end);
	SLASH_UUNAWANT1 = "/uuna";
	SlashCmdList.UUNAWANT = function()
		if frame:IsShown() then
			frame:Hide();
			if UunaDebugFrame then
				UunaDebugFrame:Hide();
			end;
			if UunaAuraFrame then
				UunaAuraFrame:Hide();
			end;
		else
			frame:Show();
			ScrollToBottom();
		end;
	end;
end;
