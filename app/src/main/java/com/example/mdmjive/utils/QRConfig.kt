package com.example.mdmjive.utils

import android.util.Base64
import org.json.JSONObject

object QRConfig {
    /**
     * Genera un código QR en formato Base64 con datos de aprovisionamiento.
     *
     * @param serverUrl URL del servidor donde se aloja el APK del MDM.
     * @param deviceId Identificador único del dispositivo.
     * @param skipEncryption Bandera para omitir la encriptación del dispositivo durante el aprovisionamiento.
     * @return Cadena codificada en Base64 lista para generar el código QR.
     */
    fun generateProvisioningQR(
        serverUrl: String,
        deviceId: String,
        skipEncryption: Boolean = true
    ): String {
        val provisioningData = JSONObject().apply {
            put(
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME",
                "com.example.mdmjive/com.example.mdmjive.receivers.MDMDeviceAdminReceiver"
            )
            put(
                "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION",
                "$serverUrl/downloads/mdm.apk"
            )
            put("android.app.extra.PROVISIONING_SKIP_ENCRYPTION", skipEncryption)
            put("serverUrl", serverUrl)
            put("deviceId", deviceId)
        }

        return Base64.encodeToString(
            provisioningData.toString().toByteArray(Charsets.UTF_8),
            Base64.DEFAULT
        )
    }
}
