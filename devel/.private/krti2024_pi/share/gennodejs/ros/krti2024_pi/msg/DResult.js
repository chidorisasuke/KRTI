// Auto-generated. Do not edit!

// (in-package krti2024_pi.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class DResult {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.is_found = null;
      this.dx = null;
      this.dy = null;
      this.dx_m = null;
      this.dy_m = null;
    }
    else {
      if (initObj.hasOwnProperty('is_found')) {
        this.is_found = initObj.is_found
      }
      else {
        this.is_found = false;
      }
      if (initObj.hasOwnProperty('dx')) {
        this.dx = initObj.dx
      }
      else {
        this.dx = 0;
      }
      if (initObj.hasOwnProperty('dy')) {
        this.dy = initObj.dy
      }
      else {
        this.dy = 0;
      }
      if (initObj.hasOwnProperty('dx_m')) {
        this.dx_m = initObj.dx_m
      }
      else {
        this.dx_m = 0.0;
      }
      if (initObj.hasOwnProperty('dy_m')) {
        this.dy_m = initObj.dy_m
      }
      else {
        this.dy_m = 0.0;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type DResult
    // Serialize message field [is_found]
    bufferOffset = _serializer.bool(obj.is_found, buffer, bufferOffset);
    // Serialize message field [dx]
    bufferOffset = _serializer.int32(obj.dx, buffer, bufferOffset);
    // Serialize message field [dy]
    bufferOffset = _serializer.int32(obj.dy, buffer, bufferOffset);
    // Serialize message field [dx_m]
    bufferOffset = _serializer.float32(obj.dx_m, buffer, bufferOffset);
    // Serialize message field [dy_m]
    bufferOffset = _serializer.float32(obj.dy_m, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type DResult
    let len;
    let data = new DResult(null);
    // Deserialize message field [is_found]
    data.is_found = _deserializer.bool(buffer, bufferOffset);
    // Deserialize message field [dx]
    data.dx = _deserializer.int32(buffer, bufferOffset);
    // Deserialize message field [dy]
    data.dy = _deserializer.int32(buffer, bufferOffset);
    // Deserialize message field [dx_m]
    data.dx_m = _deserializer.float32(buffer, bufferOffset);
    // Deserialize message field [dy_m]
    data.dy_m = _deserializer.float32(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    return 17;
  }

  static datatype() {
    // Returns string type for a message object
    return 'krti2024_pi/DResult';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'bdb57b108ed455ecab1cab6b0ba9017d';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    bool is_found
    int32 dx
    int32 dy
    float32 dx_m
    float32 dy_m
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new DResult(null);
    if (msg.is_found !== undefined) {
      resolved.is_found = msg.is_found;
    }
    else {
      resolved.is_found = false
    }

    if (msg.dx !== undefined) {
      resolved.dx = msg.dx;
    }
    else {
      resolved.dx = 0
    }

    if (msg.dy !== undefined) {
      resolved.dy = msg.dy;
    }
    else {
      resolved.dy = 0
    }

    if (msg.dx_m !== undefined) {
      resolved.dx_m = msg.dx_m;
    }
    else {
      resolved.dx_m = 0.0
    }

    if (msg.dy_m !== undefined) {
      resolved.dy_m = msg.dy_m;
    }
    else {
      resolved.dy_m = 0.0
    }

    return resolved;
    }
};

module.exports = DResult;
