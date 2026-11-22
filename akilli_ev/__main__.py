"""Demo: python -m akilli_ev"""
from akilli_ev import (BrightnessLimitedLight, LoggedLight, LumaFactory, NovaFactory,
                       RetryLight, SmartHomeFacade)


# =====================================================================
# DEMO
# =====================================================================
if __name__ == "__main__":
    luma, nova = LumaFactory(), NovaFactory()
    home = SmartHomeFacade()
    home.add_light("salon", luma)
    home.add_light("mutfak", nova)
    home.add_light("yatak odası", nova)
    home.set_thermostat(luma)

    print("--- Film sahnesi")
    home.run_scene("film")
    print("--- Geri al")
    home.undo()

    print("--- Gece modu")
    home.set_mode("gece")
    home.motion("mutfak")

    print("--- Uzakta modu")
    home.set_mode("uzakta")
    home.motion("salon")
    home.temperature(21)

    print("--- Evde modu")
    home.set_mode("evde")
    home.temperature(18)

    print("--- Dekoratör zinciri: Retry -> Sınır -> Log (arızalı Zigbee bağlantısı)")
    deco = SmartHomeFacade()
    deco.add_light("salon", LumaFactory(fail_times=2))   # ilk 2 gönderim başarısız olur
    deco.set_thermostat(NovaFactory())
    deco.wrap_light("salon", RetryLight, tries=3)
    deco.wrap_light("salon", BrightnessLimitedLight, max_percent=60)
    deco.wrap_light("salon", LoggedLight)
    print("  Zincir:", deco.describe_light("salon"))
    deco.set_light("salon", 100)

    print("--- Sıra önemlidir: Log(Sınır(x)) ile Sınır(Log(x)) farklı kaydeder")
    a = LoggedLight(BrightnessLimitedLight(NovaFactory().create_light("a"), 60))
    b = BrightnessLimitedLight(LoggedLight(NovaFactory().create_light("b")), 60)
    print(" ", a.describe()); a.set_brightness(100)
    print(" ", b.describe()); b.set_brightness(100)

    print("--- Uygunsuz sarmalama engellenir (termostata ışık dekoratörü)")
    try:
        BrightnessLimitedLight(NovaFactory().create_thermostat("x"))
    except TypeError as e:
        print("  Hata:", e)
