package com.example.mdmjive.database.dao

import androidx.room.*
import com.example.mdmjive.database.entities.DeviceInfo

@Dao
interface DeviceDao {
    @Query("SELECT * FROM devices")
    suspend fun getAllDevices(): List<DeviceInfo>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertDevice(device: DeviceInfo)

    @Query("SELECT * FROM devices WHERE deviceId = :deviceId")
    suspend fun getDevice(deviceId: String): DeviceInfo?

    @Query("UPDATE devices SET status = :status, lastSync = :lastSync WHERE deviceId = :deviceId")
    suspend fun updateDeviceStatus(deviceId: String, status: String, lastSync: Long)
}