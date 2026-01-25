function UunaAddon:RefreshAuras()
	local container = UunaAddon.AuraScrollChild;
	local children = {
		container:GetChildren()
	};
	for _, child in ipairs(children) do
		child:Hide();
		child:SetParent(nil);
	end;
	local function CreateAuraLine(data, yOffset)
		local line = CreateFrame("Frame", nil, container);
		line:SetSize(260, 20);
		line:SetPoint("TOPLEFT", 0, yOffset);
		local isUntracked = UntrackedAuras[data.spellId];
		local btn = CreateFrame("Button", nil, line);
		btn:SetSize(16, 16);
		btn:SetPoint("LEFT", 5, 0);
		local tex = btn:CreateTexture();
		tex:SetAllPoints();
		tex:SetTexture(isUntracked and "Interface\\Buttons\\UI-GroupLoot-Pass-Up" or "Interface\\Buttons\\UI-CheckBox-Check");
		btn:SetNormalTexture(tex);
		btn:SetScript("OnClick", function()
			if UntrackedAuras[data.spellId] then
				UntrackedAuras[data.spellId] = nil;
			else
				UntrackedAuras[data.spellId] = true;
			end;
			UunaAddon:RefreshAuras();
		end);
		local text = line:CreateFontString(nil, "OVERLAY", "GameFontNormal");
		text:SetPoint("LEFT", 25, 0);
		local color = isUntracked and "|cff888888" or "|cffffffff";
		text:SetText(color .. data.name .. " (" .. data.spellId .. ")|r");
		return 22;
	end;
	local y = 0;
	for i = 1, 40 do
		local data = C_UnitAuras.GetAuraDataByIndex("player", i, "HELPFUL");
		if data then
			y = y - CreateAuraLine(data, y);
		end;
	end;
	for i = 1, 40 do
		local data = C_UnitAuras.GetAuraDataByIndex("player", i, "HARMFUL");
		if data then
			y = y - CreateAuraLine(data, y);
		end;
	end;
end;
function UunaAddon:ToggleAura()
	if not UunaAuraFrame then
		local f = CreateFrame("Frame", "UunaAuraFrame", UIParent, "BasicFrameTemplateWithInset");
		f:SetSize(300, 400);
		f.title = f:CreateFontString(nil, "OVERLAY", "GameFontHighlight");
		f.title:SetPoint("CENTER", f.TitleBg, "CENTER", 0, 0);
		f.title:SetText("Aura Tracker Control");
		local scroll = CreateFrame("ScrollFrame", nil, f, "UIPanelScrollFrameTemplate");
		scroll:SetPoint("TOPLEFT", 10, -35);
		scroll:SetPoint("BOTTOMRIGHT", -30, 45);
		local child = CreateFrame("Frame", nil, scroll);
		child:SetSize(260, 1);
		scroll:SetScrollChild(child);
		UunaAddon.AuraScrollChild = child;
		local btn = CreateFrame("Button", nil, f, "GameMenuButtonTemplate");
		btn:SetSize(100, 20);
		btn:SetPoint("BOTTOM", 0, 10);
		btn:SetText("Refresh");
		btn:SetScript("OnClick", function()
			UunaAddon:RefreshAuras();
		end);
		UunaAuraFrame = f;
	end;
	if UunaAuraFrame:IsShown() then
		UunaAuraFrame:Hide();
	else
		UunaAuraFrame:SetPoint("LEFT", UunaLogFrame, "RIGHT", 10, 0);
		UunaAddon:RefreshAuras();
		UunaAuraFrame:Show();
	end;
end;
