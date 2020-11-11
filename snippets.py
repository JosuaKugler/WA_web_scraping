def read_last_in_message(driver):
    """
    Reading the last message that you got in from the chatter
    """
    for messages in driver.find_elements_by_xpath(
            "//div[contains(@class,'message-in')]"):
        try:
            message = ""
            emojis = []

            message_container = messages.find_element_by_xpath(
                ".//div[@class='copyable-text']")

            message = message_container.find_element_by_xpath(
                ".//span[contains(@class,'selectable-text invisible-space copyable-text')]"
            ).text

            for emoji in message_container.find_elements_by_xpath(
                    ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
            ):
                emojis.append(emoji.get_attribute("data-plain-text"))

        except NoSuchElementException:  # In case there are only emojis in the message
            try:
                message = ""
                emojis = []
                message_container = messages.find_element_by_xpath(
                    ".//div[@class='copyable-text']")

                for emoji in message_container.find_elements_by_xpath(
                        ".//img[contains(@class,'selectable-text invisible-space copyable-text')]"
                ):
                    emojis.append(emoji.get_attribute("data-plain-text"))
            except NoSuchElementException:
                pass

    return message, emojis