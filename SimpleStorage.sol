// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 public favNum;

    struct People {
        uint256 favNum;
        string name;
    }

    People[] public persons;

    mapping(string => uint256) public nameToFavNum;

    function store(uint256 _favNum) public returns (uint256) {
        favNum = _favNum;
        return _favNum;
    }

    function retrieve() public view returns (uint256) {
        return favNum;
    }

    function storePeople(uint256 _number, string memory _name) public {
        persons.push(People({favNum: _number, name: _name}));
        nameToFavNum[_name] = _number;
    }
}
