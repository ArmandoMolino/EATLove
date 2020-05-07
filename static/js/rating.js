function rating(rating) {
    var i, txt = "";
    for (i=1; i<6; i++){
        if( i <= rating ){
            txt += "<img src=\"https://upload.wikimedia.org/wikipedia/commons/6/63/Star%2A.svg\" width=\"25\" height=\"25\">";
        } else  {
            if( i % rating > 1 )
                txt += "<img src=\"https://upload.wikimedia.org/wikipedia/commons/e/e7/Empty_Star.svg\" width=\"25\" height=\"25\">";
            else if (i % rating >= 0.1 && i % rating < 0.5)
                txt += "<img src=\"https://upload.wikimedia.org/wikipedia/commons/6/62/Star%C2%BC.svg\" width=\"25\" height=\"25\">";
            else if (i % rating > 0.5 && i % rating <= 0.9)
                txt += "<img src=\"https://upload.wikimedia.org/wikipedia/commons/6/62/Star%C2%BC.svg\" width=\"25\" height=\"25\">";
            else
                txt += "<img src=\"https://upload.wikimedia.org/wikipedia/commons/b/b5/Star%C2%BD.svg\" width=\"25\" height=\"25\">";
        }
    }
    return txt;
}