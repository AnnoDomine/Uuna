function UunaAddon:InitMinimap()
	local minimapBtn = CreateFrame("Button", "UunaMinimapButton", Minimap);
	minimapBtn:SetSize(31, 31);
	minimapBtn:SetFrameLevel(10);
	minimapBtn:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight");
	local icon = minimapBtn:CreateTexture(nil, "BACKGROUND");
	icon:SetTexture("Interface\\Icons\\achievement_worldevent_littlehelper");
	icon:SetSize(20, 20);
	icon:SetPoint("CENTER", 0, 0);
	local border = minimapBtn:CreateTexture(nil, "OVERLAY");
	border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder");
	border:SetSize(53, 53);
	border:SetPoint("TOPLEFT", 0, 0);
	local function UpdatePosition()
		local angle = rad(UunaSettings.minimapPos);
		local x = cos(angle) * 80;
		local y = sin(angle) * 80;
		minimapBtn:SetPoint("CENTER", Minimap, "CENTER", x, y);
	end;
	minimapBtn:RegisterForDrag("LeftButton");
	minimapBtn:SetScript("OnDragStart", function(self)
		self:SetScript("OnUpdate", function()
			local xpos, ypos = GetCursorPosition();
			local xmin, ymin = Minimap:GetLeft(), Minimap:GetBottom();
			local scale = Minimap:GetEffectiveScale();
			local x = xmin + 70 - xpos / scale;
			local y = ypos / scale - (ymin + 70);
			UunaSettings.minimapPos = deg(atan2(y, x));
			UpdatePosition();
		end);
	end);
	minimapBtn:SetScript("OnDragStop", function(self)
		self:SetScript("OnUpdate", nil);
	end);
	minimapBtn:SetScript("OnClick", function(self, button)
		if button == "LeftButton" then
			if UunaLogFrame:IsShown() then
				UunaLogFrame:Hide();
				if UunaDebugFrame then
					UunaDebugFrame:Hide();
				end;
				if UunaAuraFrame then
					UunaAuraFrame:Hide();
				end;
			else
				UunaLogFrame:Show();
			end;
		end;
	end);
	UpdatePosition();
end;
