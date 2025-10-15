- 
Adress bus width = 10
                    
                     => 2^10 B = 1KB
Data bw = 8 bits = 1B

Adress size: 0000h -> (2^10 - 1) = 03FFh

- 
Adress bw = 15

                    => memory size = 1/2 * 2^15 = 2^14 B = 2^4 KB = 16 KB
Data bw = 4b = 1/2 B

Adress size: 0000h -> (2^14 - 1) = 00000h -> 01FFFh
    
    0011 1111 1111 1111 = 03FFFF

- 
Memory size = 1MB = 2^20 B = 1 B * 2^20
    
    -> 1 B = Bus data width, 20 = adress bus width

Address space: 00000h -> 2^20 - 1 = 1111 1111 1111 1111 1111 = 0FFFFFh

000000h -> 0FFFFFh

- 

data bus width = 8n = 1B

Adress space: 0000h - 0FFFh

0FFFh = 0111 1111 1111 = 11 bits of 1 => 2^11 mem size

memory size = 2^11 = 2*2^10 B = 2 KB

Adress bus width = 11

- 

Adress bus width = 24

            => Memory size = 1b * 2^24 = 2^24 b= 2^3 * 2^21b = 2^21 B = 2MB
Data bus width = 1b

=> Adress space: 0000h -> (2^21 - 1)

2^21 = 0001 1111 1111 1111 1111 1111

0000000h -> 01FFFFFh

- 

Adress bus width = 32

                => Memory size = 1b * 2^32 = 2^32 b = 2^3 * 2^29 b = 2^29 B = 2^9 MB
Data bus width = 1b

Adress size: 0h -> 2^29 - 1= 00000000h -> 01FFFFFFFh

2^29 = 0001 1111 1111 1111 1111 1111 1111 1111

        01   F    F    F    F    F    F    F

- 

Data bus width = 1b = 2^-3 B

Adress size: 0000h -> FFFFh

FFFFh = 1111 1111 1111 1111 = 2^16 -1 (16 bits of 1)

=> memory size = 2^16 B = 2^6 KB

                   |
                   |-> 2^19 * 2^-3 => 2^19 => adress bus width = 19

- 

Adress space: 000000 - 03FFFFh

0011 1111 1111 1111 1111 = 2^18 - 1

=> memory size = 2^18 B = 2^8 KB

2^18 B = 2^18 * 1B 

                => data bus width = 1B = 8b
                   adress bus width = 18

- 


memory size = 8 KB = 2^3 KB = 2^13 B = 2^13 * 1B

            => data bus width = 1B = 8 bits
               adress bus width = 13


=> Adress space: 0h -> (2^13 - 1) -> 00000h -> 01FFFFh

                        |-> 0001 1111 1111 1111
                             01    F    F    F
    

- 

Memory size = 1 GB = 2^30 b = 2^3 * 2^27 b = 2^27 B = 2^7 B
                                            
                                            |-> 2^27 * 1 B => Adress bus width = 27

Data bus width = 8b = 1 B

Adress space: 000h -> (2^27 - 1)

                        |-> 0111 1111 1111 1111 1111 1111 1111

=> 00000000h -> 07FFFFFFh


- 


Adress bus width = 18

Data bus width = 8b = 1B

=> Memory size = 2^18 * 1B = 2^18 B = 2^8 KB

-> Adress space: 000..0h -> 2^18-1 -> 000000h -> 03FFFFh

                            |-> 0011 1111 1111 1111 1111
                                 03   F    F    F    F

- 

Memory size = 128 MB = 2^7 Mb = 2^7 * 2^20 b = 2^27b = 2^3 b * 2^24b = 2^24 B = 2^4 MB = 16 MB

                                                                    |-> 2^24 * 1B

=> Data bus width = 8b = 1B

Address bus width = 24

Adress space : 0..0h -> (2^24 - 1) => 0000000h -> 0FFFFFFh

                                    |-> 1111 1111 1111 1111 1111 1111
                                          F   F    F    F    F    F

- 

Adress space : 000000h -> 0FFFFFFh = 1111 1111 1111 1111 1111 = 2^20 - 1

=> Memory size = 2^20 B = 1 MB

                  |->  2^20 * 1B => Adress bus width = 20
                                    Data bus width = 8b = 1B

- 

Memory size = 512 Mb = 2^9 Mb= 2^9 * 2^20b = 2^29b = 2^3 * 2^26 b = 2^26 B = 2^6 Mb

=> Data bus width = 1B = 8b

Adress bus width = 26

Adress space: 0..0h -> (2^26 - 1) -> 00000000h -> 03FFFFFFh

                        |-> 0011    1111 1111 1111 1111 1111 1111
                             03       F    F    F    F   F    F


- 
                    
Adress bus width = 28

                        => Memory size = 2^28 * 1B = 2^28 B = 2^8 MB
Data bus width = 8b = 1B

Adress space: 0..0h -> (2^28 - 1) => 00000000h -> 0FFFFFFFh
                        
                        |-> 1111 1111 1111 1111 1111 1111 1111


- 

Adress bus width = 25

                            => Memory size = 2^25 * 2^-3 B = 2^22 B = 4MB
Data bus width = 1b = 2^-3 B

Adress space : 0..0h -> (2^22 - 1) -> 0000000h -> 03FFFFFh

                        |-> 0011 1111 1111 1111 1111 1111

- 

Adress space: 00000000h -> 03FFFFFFh

                            |-> 0011 1111 1111 1111 1111 1111 1111 = 2^26 - 1

Memory size = 2^26B = 2^6 MB

                |-> 2^26 * 1B => Data bus width = 1B = 8b
                                 Adress bus width = 26


- 

Adress space : 000000h -> 05FFFFh
                        
                            |-> 0101 1111 1111 1111 1111 = 2^18 + 2^17 -1

=> Memory size: (2^18 + 2^17)B = 2^17(2+1)B = 3 * 2^17B = 3 * 2^7 * 2^10 B = 3 * 2^7 KB = 381 KB

                                            |-> Data bus width = 3b
                                                Adress bus width = 17

- 

Memory size = 2GB = 2 * 2^30 b = 2^31 b = 2^3 * 2^28 b = 2^28 B

                                                        |-> 2^28 * 1B => Data bus width = 8b
                                                                         Adress bus width = 28

Adress space : 0..0h -> 2^28 - 1 -> 00000000h -> 0FFFFFFFh

                        |-> 1111 1111 1111 1111 1111 1111 1111

- 

Adress bus width = 40

                                => Memory size = 2^40 * 2^-3 = 2^37 B = 128Gb
Data bus width = 1b = 2^-3 B

Adress space : 0..0h -> 2^37 -1 -> 00000000000 -> 01FFFFFFFFF

                        |-> 0001 1111 1111 1111 1111 1111 1111 1111 1111 1111

                
- 

Data bus width = 8b = 1B

Adress space : 0000h -> 03FFh

                        |-> 0011 1111 1111 = (2^10 - 1)
                                                |-> 2^10 B = 1KB
                                                    |-> 2^10 * 1B
                                                        |-> address bus width = 10


- 

Address bus width = 16

Data bus width = 9b = 1 + 8 = 1b + 1B

Memory size = 2^16 * 2^9b = 2^19 * (2^3 + 1b) = 2^19 * 2^3 b + 2^19b = 2^19 B + 2^19 * 2^-3 B = 
                                        2^19 B + 2^16 B = 2^16 * (2^3 + 1) B = 2^16 * 9 B = 9 * 2^6 KB

Adress space: 0..0h -> (2^19 + 2^16 - 1)- > 000000h -> 08FFFFh

                        |-> 10000 1111 1111 1111 1111

- 

Memory size = 128 KB = 2^7 KB = 2^7 KB = 2^7 * 2^10B = 2^17 B = 2^17 * 1B

                        => Data bus width = 1B = 8b
                           Address bus width = 17


Adress space : 0..0h -> (2^17 - 1) -> 0000000h -> 01FFFFh

                        |-> 0001 1111 1111 1111 1111

- 

Adress space : 00000000h -> 1FFFFFFFh

    => 0001 1111 1111 1111 1111 1111 1111 1111 = 2^29 - 1 -> 2^29 = 2^32 * 2^-3 

Memory size = 2^29 B = 2^9 MB = 512 MB

Data bus width = 1b = 2^-3 B -> Address bus width = 32

- 

Address bus width = 22


                        => Memory size = 2^22 * 1B = 2^22 B = 4MB
Data bus width = 8b = 1B 

Address size: 0..0h -> (2^22 - 1) -> 0000000h -> 03FFFFFh

                        |-> 0011 1111 1111 1111 1111 1111


- 

Memory size = 256 KB = 2^8 KB = 2^8 * 2^10 B = 2^18 B = 2^18 * 1B 

                                                            => Data bus width = 1B = 8b
                                                               Address bus width = 18

Address size: 0..0h -> 2^18 -1 -> 000000h -> 03FFFFh


                        |-> 0011 1111 1111 1111 1111


