package com.example.mdmjive.repository

import com.example.mdmjive.database.DeviceDao
import com.example.mdmjive.network.ApiService
import android.provider.Settings
import android.os.Build
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import android.util.Log

class DeviceRepository(
    private val apiService: ApiService,
    private val deviceDao: DeviceDao
) {

    companion object {
        private const val TAG = "DeviceRepository"
        private const val SYNC_TIME = System.currentTimeMillis()
    }

    // Obtener ID único del dispositivo
    private fun getDeviceId(context: android.content.Context): String {
        return Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ANDROID_ID
        )
    }

    // Registrar dispositivo
    suspend fun registerDevice(context: android.content.Context) {
        val deviceInfo = DeviceInfo(
            deviceId = getDeviceId(context),
            model = Build.MODEL,
            manufacturer = Build.MANUFACTURER,
            osVersion = Build.VERSION.RELEASE
        )

        try {
            val response = apiService.registerDevice(deviceInfo)
            if (response.isSuccessful) {
                deviceDao.insertDeviceInfo(
                    DeviceInfoEntity(
                        deviceId = deviceInfo.deviceId,
                        status = "REGISTERED",
                        lastSync = SYNC_TIME
                    )
                )
                Log.d(TAG, "Dispositivo registrado exitosamente")
            } else {
                Log.e(TAG, "Error en el registro del dispositivo: ${response.message()}")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error al registrar dispositivo: ${e.localizedMessage}")
        }
    }

    // Actualizar estado
    suspend fun updateDeviceStatus(context: android.content.Context, newStatus: String) {
        val deviceId = getDeviceId(context)
        val status = DeviceStatus(
            deviceId = deviceId,
            status = newStatus,
            lastSync = SYNC_TIME
        )

        try {
            val response = apiService.updateStatus(status)
            if (response.isSuccessful) {
                deviceDao.updateDeviceStatus(deviceId, newStatus, SYNC_TIME)
                Log.d(TAG, "Estado del dispositivo actualizado")
            } else {
                Log.e(TAG, "Error al actualizar el estado del dispositivo: ${response.message()}")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error al actualizar el estado del dispositivo: ${e.localizedMessage}")
        }
    }

    // Sincronizar con servidor
    suspend fun syncWithServer() = withContext(Dispatchers.IO) {
        try {
            val localDevices = deviceDao.getAllDevices()
            localDevices.forEach { device ->
                val status = DeviceStatus(
                    deviceId = device.deviceId,
                    status = device.status,
                    lastSync = device.lastSync
                )
                val response = apiService.updateStatus(status)
                if (response.isSuccessful) {
                    Log.d(TAG, "Dispositivo ${device.deviceId} sincronizado exitosamente")
                } else {
                    Log.e(TAG, "Error al sincronizar dispositivo ${device.deviceId}: ${response.message()}")
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error al sincronizar con el servidor: ${e.localizedMessage}")
        }
    }
}
