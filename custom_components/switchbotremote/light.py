from homeassistant.components.light import LightEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from .client.remote import SupportedRemote

from .const import DOMAIN


class SwitchBotRemoteLight(LightEntity, RestoreEntity):
    _attr_has_entity_name = False

    def __init__(self, hass: HomeAssistant, sb: SupportedRemote, _id: str, name: str, options: dict = {}) -> None:
        super().__init__()
        self._hass = hass
        self.sb = sb
        self._unique_id = _id
        self._device_name = name
        self._power_sensor = options.get("power_sensor", None)
        self._state = STATE_OFF
        self._source = None
        self._brightness = None

    async def send_command(self, *args):
        await self._hass.async_add_executor_job(self.sb.command, *args)

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer="switchbot",
            name=self._device_name,
            model="Switchbot Remote Light",
        )
    
    @property
    def is_on(self):
        """Check if Tuya light is on."""
        return self._state
    
    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None:
            self._state = last_state.state

    async def async_turn_on(self, **kwargs):
        """Send the power on command."""
        await self.send_command("turnOn")
        self._state = STATE_ON

    async def async_turn_on(self, **kwargs):
        """Send the power on command."""
        await self.send_command("turnOff")
        self._state = STATE_ON


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    remotes = hass.data[DOMAIN][entry.entry_id]

    climates = [
        SwitchBotRemoteLight(remote, remote.id, remote.name)
        for remote in filter(lambda r: r.type == "Light", remotes)
    ]

    async_add_entities(climates)
