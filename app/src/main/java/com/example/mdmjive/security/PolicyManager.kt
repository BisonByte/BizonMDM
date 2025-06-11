package com.example.mdmjive.security

import android.app.admin.DevicePolicyManager
import android.content.Context
import android.content.ComponentName
import android.util.Log

class PolicyManager(private val context: Context) {
    private val dpm = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
    private val componentName = ComponentName(context, "com.example.mdmjive.receivers.MDMDeviceAdminReceiver")

    fun enforcePasswordPolicy() {
        try {
            dpm.apply {
                setPasswordQuality(componentName, DevicePolicyManager.PASSWORD_QUALITY_COMPLEX)
                setPasswordMinimumLength(componentName, 8)
                setPasswordMinimumLetters(componentName, 1)
                setPasswordMinimumNumeric(componentName, 1)
            }
            Log.d("MDM", "Política de contraseña aplicada")
        } catch (e: Exception) {
            Log.e("MDM", "Error aplicando política de contraseña: ${e.message}")
        }
    }

    fun disableCamera(disable: Boolean) {
        try {
            dpm.setCameraDisabled(componentName, disable)
            Log.d("MDM", "Cámara ${if(disable) "deshabilitada" else "habilitada"}")
        } catch (e: Exception) {
            Log.e("MDM", "Error configurando cámara: ${e.message}")
        }
    }

    fun enforceEncryption() {
        try {
            if (dpm.getStorageEncryptionStatus() != DevicePolicyManager.ENCRYPTION_STATUS_ACTIVE) {
                dpm.setStorageEncryption(componentName, true)
            }
            Log.d("MDM", "Encriptación configurada")
        } catch (e: Exception) {
            Log.e("MDM", "Error configurando encriptación: ${e.message}")
        }
    }

    fun restrictApps(packageNames: List<String>) {
        try {
            dpm.setLockTaskPackages(componentName, packageNames.toTypedArray())
            Log.d("MDM", "Restricción de apps aplicada")
        } catch (e: Exception) {
            Log.e("MDM", "Error restringiendo apps: ${e.message}")
        }
    }

    fun setScreenTimeout(timeoutMs: Long) {
        try {
            dpm.setMaximumTimeToLock(componentName, timeoutMs)
            Log.d("MDM", "Timeout de pantalla configurado")
        } catch (e: Exception) {
            Log.e("MDM", "Error configurando timeout: ${e.message}")
        }
    }

    fun disableFactoryReset() {
        try {
            dpm.addUserRestriction(componentName, android.os.UserManager.DISALLOW_FACTORY_RESET)
            Log.d("MDM", "Restablecimiento de fábrica deshabilitado")
        } catch (e: Exception) {
            Log.e("MDM", "Error deshabilitando restablecimiento: ${e.message}")
        }
    }

    fun lockBrightness() {
        try {
            dpm.setSystemSetting(componentName, android.provider.Settings.System.SCREEN_BRIGHTNESS, "255")
            dpm.setSystemSetting(componentName, android.provider.Settings.System.SCREEN_BRIGHTNESS_MODE,
                android.provider.Settings.System.SCREEN_BRIGHTNESS_MODE_MANUAL.toString())
            dpm.addUserRestriction(componentName, android.os.UserManager.DISALLOW_CONFIG_BRIGHTNESS)
            Log.d("MDM", "Brillo fijado al 100% y bloqueado")
        } catch (e: Exception) {
            Log.e("MDM", "Error configurando brillo: ${e.message}")
        }
    }

    fun lockGPS() {
        try {
            dpm.setSecureSetting(componentName, android.provider.Settings.Secure.LOCATION_MODE,
                android.provider.Settings.Secure.LOCATION_MODE_HIGH_ACCURACY.toString())
            dpm.addUserRestriction(componentName, android.os.UserManager.DISALLOW_CONFIG_LOCATION)
            Log.d("MDM", "GPS forzado y bloqueado")
        } catch (e: Exception) {
            Log.e("MDM", "Error configurando GPS: ${e.message}")
        }
    }

    fun lockDateTime() {
        try {
            dpm.setGlobalSetting(componentName, android.provider.Settings.Global.AUTO_TIME, "1")
            dpm.setGlobalSetting(componentName, android.provider.Settings.Global.AUTO_TIME_ZONE, "1")
            dpm.addUserRestriction(componentName, android.os.UserManager.DISALLOW_CONFIG_DATE_TIME)
            Log.d("MDM", "Fecha y hora configuradas automáticamente y bloqueadas")
        } catch (e: Exception) {
            Log.e("MDM", "Error configurando fecha/hora: ${e.message}")
        }
    }
}
