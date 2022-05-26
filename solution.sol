//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract solution {

  uint totalDonations;
  uint public singleDonation; // the amount of donations
//   address owner; // contract creator's address
  string public name; // Contract creator's name
  string public event1;

constructor(string memory _name, uint _donation, string memory _event){
  name = _name;
  singleDonation = _donation;
  totalDonations += _donation;
  event1 = _event;
}

  //public function to make donate
  // function donate(string memory _name,uint _donation) public {
  //   name.push(_name);
  //   singleDonation.push(_donation);
  //   totalDonations += _donation;
  // }
//   function donate(string memory _name,uint _donation) public payable {
//     (bool success,) = owner.call{value: _donation}('');
//     require(success, "Failed to send money");
//     name = _name;
//     totalDonations += msg.value;
//   }

  //public function to return name of person
  function nameviewer() view public returns(string memory) {
    return name;
  }

  // public function to return total of donations
  function getTotalDonations() view public returns(uint) {
    return totalDonations;
  }
}