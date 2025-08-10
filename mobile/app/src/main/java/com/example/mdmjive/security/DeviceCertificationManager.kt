package com.example.mdmjive.security

data class DeviceIntegrityResult(
    val isRooted: Boolean,
    val isEmulator: Boolean,
    val hasUnknownSources: Boolean,
    val integrityScore: Int
)

import android.content.Context
import android.provider.Settings
import android.util.Log
import com.example.mdmjive.network.ApiService
import com.example.mdmjive.network.models.DeviceStatus
import kotlinx.coroutines.runBlocking
import com.example.mdmjive.utils.TokenManager

class DeviceCertificationManager(
    private val context: Context,
    private val apiService: ApiService
) {
    fun validateDeviceIntegrity(): DeviceIntegrityResult {
        val isRooted = SecurityChecker.isDeviceRooted()
        val isEmulator = SecurityChecker.isRunningOnEmulator()
        val hasUnknownSources = SecurityChecker.hasUnknownSources(context)
        val integrityScore = calculateIntegrityScore(isRooted, isEmulator, hasUnknownSources)

        val statusValue = if (isRooted || isEmulator || hasUnknownSources) "COMPROMISED" else "OK"
        val deviceStatus = DeviceStatus(
            deviceId = getDeviceId(),
            status = statusValue,
            rootAttempt = isRooted,
            emulator = isEmulator,
            unknownSources = hasUnknownSources
        )
        val token = TokenManager.getToken(context)
        if (token != null) {
            try {
                val bearer = "Bearer $token"
                runBlocking { apiService.updateStatus(bearer, deviceStatus) }
            } catch (e: Exception) {
                Log.e("DeviceCertificationManager", "Failed to update status", e)
            }
        } else {
            Log.e("DeviceCertificationManager", "Token no disponible")
        }

        return DeviceIntegrityResult(
            isRooted = isRooted,
            isEmulator = isEmulator,
            hasUnknownSources = hasUnknownSources,
            integrityScore = integrityScore
        )
    }

    private fun calculateIntegrityScore(
        isRooted: Boolean,
        isEmulator: Boolean,
        hasUnknownSources: Boolean
    ): Int {
        var score = 100

        if (isRooted) score -= 40
        if (isEmulator) score -= 30
        if (hasUnknownSources) score -= 20

        return score.coerceAtLeast(0) // Asegura que el puntaje no sea negativo
    }

    private fun getDeviceId(): String =
        Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
}
