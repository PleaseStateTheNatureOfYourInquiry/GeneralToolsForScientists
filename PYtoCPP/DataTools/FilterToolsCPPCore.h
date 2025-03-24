#ifndef FILTERTOOLSCPPCORE_H
#define FILTERTOOLSCPPCORE_H


class FilterToolsCPPCore {

    public:

        FilterToolsCPPCore ();
        ~FilterToolsCPPCore ();
                
        void passAverageFilter ( 
            float listOfNumbers [1], //1
            float listOfNumbersFiltered [1], //2
            int numberOfElements, //3
            int widthOfWindow //4           
        );

};


#endif
