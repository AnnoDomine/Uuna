UunaLogHistory = UunaLogHistory or {};
UunaDebugHistory = {};
UntrackedAuras = UntrackedAuras or {};
UunaCustomQuests = UunaCustomQuests or {};
UunaAddon = {};
UunaAddon.SPECIES_ID = 2136;
local playerAuraSnapshot = {};
local function InitSettings()
	if not UunaSettings then
		UunaSettings = {
			minimapPos = 45,
			showMinimapIcon = true,
			mainPos = {
				"CENTER",
				0,
				0
			},
			debugPos = {
				"TOP",
				0,
				-5
			},
			auraPos = {
				"LEFT",
				10,
				0
			}
		};
	end;
end;
local function GetAuraSnapshot(unit)
	local snapshot = {};
	for i = 1, 40 do
		local data = C_UnitAuras.GetAuraDataByIndex(unit, i);
		if data then
			local success, sID = pcall(function()
				return data.spellId;
			end);
			local nameSuccess, nName = pcall(function()
				return data.name;
			end);
			if success and nameSuccess and type(sID) == "number" and type(nName) == "string" then
				snapshot[sID] = nName;
			end;
		end;
	end;
	return snapshot;
end;
function UunaAddon:AddToStory(name, text, do_not_log)
	local safeName = tostring(name or "");
	local safeText = tostring(text or "");
	local timestamp = date("%d.%m. %H:%M");
	local entry = "";
	if safeName == "" then
		entry = "|cff888888" .. safeText .. "|r";
	elseif safeName == "AURA" then
		entry = "|cff00ff00[" .. timestamp .. "] Aura:|r " .. safeText;
	elseif safeName == "SECRET" then
		entry = "|cff00ffff[" .. timestamp .. "] SECRET:|r " .. safeText;
	else
		entry = "|cffffd100[" .. timestamp .. "] " .. safeName .. ":|r " .. safeText;
	end;
	entry = tostring(entry);
	if not do_not_log then
		table.insert(UunaLogHistory, entry);
		if #UunaLogHistory > 100 then
			table.remove(UunaLogHistory, 1);
		end;
	end;
	if UunaAddon.UpdateStoryUI then
		pcall(function()
			UunaAddon:UpdateStoryUI(entry);
		end);
	end;
end;
UunaAddon.currentDebugIndex = 1;
function UunaAddon:AddToDebug(event, ...)
	local timestamp = date("%H:%M:%S");
	local args = {
		...
	};
	local argString = "";
	for i, val in ipairs(args) do
		local success, strVal = pcall(function()
			return tostring(val);
		end);
		argString = argString .. string.format("\n|cffaaaaaaArg%d:|r %s", i, (success and type(strVal) == "string" and strVal or "SecretData"));
	end;
	local info = string.format("|cffffff00Event:|r %s\n|cff00ffffTime:|r %s%s", event, timestamp, argString);
	table.insert(UunaDebugHistory, info);
	if #UunaDebugHistory > 10 then
		table.remove(UunaDebugHistory, 1);
	end;
	UunaAddon.currentDebugIndex = #UunaDebugHistory;
	if UunaAddon.UpdateDebugUI then
		UunaAddon:UpdateDebugUI();
	end;
end;
local f = CreateFrame("Frame");
local function SafeRegister(event)
	pcall(function()
		f:RegisterEvent(event);
	end);
end;
SafeRegister("ADDON_LOADED");
SafeRegister("CHAT_MSG_MONSTER_SAY");
SafeRegister("CHAT_MSG_MONSTER_EMOTE");
SafeRegister("CHAT_MSG_SAY");
SafeRegister("CHAT_MSG_CHANNEL");
SafeRegister("UPDATE_UI_WIDGET");
SafeRegister("SCENARIO_UPDATE");
SafeRegister("WORLD_STATE_VALUES_SET");
SafeRegister("VIGNETTE_EVENT_AVAILABLE");
SafeRegister("CHAT_MSG_ADDON");
SafeRegister("QUEST_LOG_UPDATE");
C_ChatInfo.RegisterAddonMessagePrefix("MidnightSecret");
C_ChatInfo.RegisterAddonMessagePrefix("UunaLovesYou");
f:RegisterUnitEvent("UNIT_AURA", "player", "pet");
SafeRegister("SOUNDKIT_FINISHED");
SafeRegister("UNIT_SPELLCAST_SENT");
f:SetScript("OnEvent", function(self, event, ...)
	UunaAddon:AddToDebug(event, ...);
	local arg1, arg2, arg3, arg4 = ...;
	if event == "ADDON_LOADED" and arg1 == "UunaWantSomething" then
		InitSettings();
		playerAuraSnapshot = GetAuraSnapshot("player");
		if UunaAddon.InitUI then
			UunaAddon:InitUI();
		end;
		if UunaAddon.InitMinimap then
			UunaAddon:InitMinimap();
		end;
		C_Timer.After(0.5, function()
			UunaAddon:AddToStory("", "------------------------------------", true);
			UunaAddon:AddToStory("", "--- Session Start: " .. date("%d.%m. %H:%M") .. " ---", true);
		end);
	elseif event == "QUEST_LOG_UPDATE" then
		if UunaQuestFrame and UunaQuestFrame:IsShown() then
			UunaAddon:RefreshQuestList();
		end;
	elseif event == "UPDATE_UI_WIDGET" then
		local widgetData = arg1;
		if type(widgetData) == "table" and widgetData.widgetID then
			local wID = widgetData.widgetID;
			if wID == 8122 or wID == 8123 then
				local text = "Update";
				if widgetData.widgetType == 2 then
					local visInfo = C_UIWidgetManager.GetTextWithStateWidgetVisualizationInfo(wID);
					if visInfo and visInfo.text then
						text = visInfo.text;
					end;
				elseif widgetData.widgetType == 8 then
					local barInfo = C_UIWidgetManager.GetProgressBarWidgetVisualizationInfo(wID);
					if barInfo then
						text = barInfo.barValue .. " / " .. barInfo.barMax;
					end;
				end;
				UunaAddon:AddToStory("SECRET", "Widget [" .. wID .. "]: " .. text);
			end;
		end;
	elseif event == "CHAT_MSG_ADDON" then
		if arg1 == "MidnightSecret" or arg1 == "UunaLovesYou" then
			UunaAddon:AddToStory("SECRET", "AddonMsg [" .. arg1 .. "]: " .. tostring(arg2));
		end;
	elseif event == "VIGNETTE_EVENT_AVAILABLE" then
		UunaAddon:AddToStory("SECRET", "Vignette Detected! (ID: " .. tostring(arg1) .. ")");
	elseif event == "WORLD_STATE_VALUES_SET" or event == "SCENARIO_UPDATE" then
		UunaAddon:AddToStory("SECRET", "World/Scenario State Update");
	elseif event == "UNIT_SPELLCAST_SENT" and arg1 == "player" then
		UunaAddon:AddToStory("SECRET", "Spell Sent: " .. tostring(arg2));
	elseif event == "UNIT_AURA" then
		if arg1 == "player" then
			local newSnapshot = GetAuraSnapshot("player");
			for id, name in pairs(newSnapshot) do
				if not playerAuraSnapshot[id] and (not UntrackedAuras[id]) then
					UunaAddon:AddToStory("AURA", "|cff00ff00Gained:|r " .. name .. " (" .. id .. ")");
				end;
			end;
			for id, name in pairs(playerAuraSnapshot) do
				if not newSnapshot[id] and (not UntrackedAuras[id]) then
					UunaAddon:AddToStory("AURA", "|cffff0000Lost:|r " .. name .. " (" .. id .. ")");
				end;
			end;
			playerAuraSnapshot = newSnapshot;
			if UunaAuraFrame and UunaAuraFrame:IsShown() then
				UunaAddon:RefreshAuras();
			end;
		end;
	else
		pcall(function(text, name)
			if text then
				local tLow = string.lower(tostring(text));
				local nLow = string.lower(tostring(name or ""));
				if tLow:find("uuna") or nLow:find("uuna") then
					UunaAddon:AddToStory(name, text);
				end;
			end;
		end, arg1, arg2);
	end;
end);
