-- Function to get enabled domains, filtering out specific blacklist items
function get_enabled_domains()
    -- Execute the 'hosts enabled' command
    local command = "hosts enabled"
    local output = hs.execute(command, true) -- The second argument 'true' ensures the command runs in a UTF-8 environment

    -- Define blacklist
    local blacklist = {
        ["broadcasthost"] = true,
        ["localhost"] = true
    }

    -- Parse the output and filter domains
    local domains = {}
    for line in string.gmatch(output, "[^\r\n]+") do
        local domain = string.match(line, "%S+%s+(%S+)")
        if domain and not blacklist[domain] then
            table.insert(domains, {text = domain, subText = "Block this domain"})
        end
    end

    return domains
end

-- Function to handle domain selection
local function domainSelectionCallback(choice)
    if not choice then
        hs.alert.show("No selection made")
        return
    end
    local selectedDomain = choice.text
    hs.alert.show("You selected: " .. selectedDomain)
    -- Proceed to duration input
    hs.focus()
    inputDuration(selectedDomain)
end


-- Function to input duration
function inputDuration(domain)
    local option, text = hs.dialog.textPrompt("Enter Duration", "Specify the blocking duration for " .. domain, "", "OK", "Cancel")
    if option == "OK" then
        -- Parameters for the POST request
        local url = "http://localhost:" .. 2999 .. "/unblock"  -- Make sure PORT is defined or directly include the port number
        local headers = {["Content-Type"] = "application/json"}
        local data = hs.json.encode({domain = domain, duration_string = text})

        -- Sending the POST request
        hs.http.doAsyncRequest(url, "POST", data, headers, function(status, response)
            if status == 200 then
                hs.alert.show("Successfully blocked " .. domain .. " for " .. text)
            else
                hs.alert.show("Failed to block domain. Status: " .. status)
            end
            print(response)  -- This will print the server response to the Hammerspoon Console
        end)
    else
        hs.alert.show("No duration entered or cancelled")
    end
end



local unblockSiteChooser = hs.chooser.new(domainSelectionCallback)

function handleUnblockHotkey()
    unblockSiteChooser:choices(get_enabled_domains())
    unblockSiteChooser:show()
end

return handleUnblockHotkey
